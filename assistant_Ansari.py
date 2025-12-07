# app_webrtc.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, RTCConfiguration
import numpy as np
import av
import tempfile
import soundfile as sf
import os
import time
import speech_recognition as sr
from gtts import gTTS
import threading

st.set_page_config(page_title="Ansari Live (webrtc)", layout="centered")

st.title("Ansari — Live Microphone (webrtc)")

st.markdown(
    """
This app captures microphone audio from your browser (WebRTC), runs speech recognition on short chunks,
and generates TTS responses. **Note:** If you get errors about `av` or `ffmpeg`, see the deployment notes below.
"""
)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Shared state (simple thread-safe holder)
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_text = ""
        self.last_tts_path = None
        self.last_time = 0.0

SHARED = SharedState()

# Audio processor that accumulates audio frames and runs recognition on ~2s chunks
class ASRProcessor(AudioProcessorBase):
    def __init__(self):
        self.sample_rate = 48000  # default WebRTC sample rate
        self.buffer = np.zeros((0,), dtype=np.int16)
        self.recognizer = sr.Recognizer()
        self.min_chunk_seconds = 2.0  # run ASR every ~2 seconds
        self.channel_count = 1

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert incoming frame to mono int16 numpy array
        frame_rate = frame.sample_rate
        array = frame.to_ndarray()  # shape (channels, samples)
        # convert to mono by averaging channels if needed
        if array.ndim > 1:
            audio_mono = array.mean(axis=0)
        else:
            audio_mono = array
        # Ensure int16
        audio_int16 = audio_mono.astype(np.int16)

        # append to buffer
        self.buffer = np.concatenate((self.buffer, audio_int16))

        # If buffer long enough, perform recognition in a background thread
        if len(self.buffer) >= int(frame_rate * self.min_chunk_seconds):
            buf_copy = self.buffer.copy()
            self.buffer = np.zeros((0,), dtype=np.int16)
            threading.Thread(target=self._process_chunk, args=(buf_copy, frame_rate), daemon=True).start()

        return frame

    def _process_chunk(self, samples: np.ndarray, sr_rate: int):
        """Write samples to temp wav and run speech_recognition; then produce TTS file."""
        try:
            tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            tmp_wav.close()
            # write as 16-bit PCM mono
            sf.write(tmp_wav.name, samples, sr_rate, subtype='PCM_16')

            # Use speech_recognition to read the wav file
            with sr.AudioFile(tmp_wav.name) as source:
                audio = self.recognizer.record(source)

            # Call Google ASR (free recognizer) — may raise exceptions on failure
            try:
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError as e:
                text = f"[ASR request error: {e}]"

            # update shared state
            with SHARED.lock:
                if text:
                    SHARED.last_text = text
                    SHARED.last_time = time.time()
                    # generate TTS reply (simple echo for now; you can change logic)
                    reply = self._decide_reply(text)
                    tts_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts_tmp.close()
                    gTTS(text=reply, lang="en").save(tts_tmp.name)
                    # store path
                    SHARED.last_tts_path = tts_tmp.name
            # cleanup
            try:
                os.unlink(tmp_wav.name)
            except:
                pass
        except Exception as e:
            # keep failures quiet but print to server logs
            print("ASR chunk error:", e)

    def _decide_reply(self, text: str) -> str:
        """Simple command handler — extend as needed."""
        t = text.lower()
        if "how are you" in t:
            return "I am fine, thank you. How are you?"
        if "ansari" in t:
            return "Yes, I am here."
        if "open google" in t:
            return "I cannot open browser tabs from the server, but you can click the link in the app."
        if "play" in t:
            return "I can not play music from server. Use the music links in the app."
        if "stop" in t or "exit" in t:
            return "Okay, stopping. Close the tab when ready."
        return "I heard: " + text

# Start WebRTC streamer
webrtc_ctx = webrtc_streamer(
    key="ansari-live",
    mode="SENDRECV",
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=ASRProcessor,
    async_processing=True,
    desired_playing_state=True,
)

st.markdown("**Controls:** Allow microphone in the browser when requested. Speak clearly; recognition runs every ~2 seconds.")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Last recognized speech")
    last_text_placeholder = st.empty()
    last_time_placeholder = st.empty()

with col2:
    st.subheader("TTS")
    play_button = st.empty()

# clickable helper link for web actions
st.markdown("[Open Google in a new tab](https://www.google.com)")

# UI updater loop (non-blocking)
def ui_update():
    with SHARED.lock:
        lt = SHARED.last_text
        tpath = SHARED.last_tts_path
        ttime = SHARED.last_time

    if lt:
        last_text_placeholder.markdown(f"**{lt}**")
        last_time_placeholder.markdown(f"recognized at: {time.strftime('%H:%M:%S', time.localtime(ttime))}")
    else:
        last_text_placeholder.markdown("_No speech recognized yet._")
        last_time_placeholder.markdown("")

    if tpath and os.path.exists(tpath):
        # show audio player
        try:
            play_button.audio(tpath)
        except Exception as e:
            play_button.write("TTS ready (error showing player).")
    else:
        play_button.write("_No TTS yet._")

# Run UI update periodically while app is open
ui_update()
# (Streamlit re-runs this script on events; no infinite loop here)
