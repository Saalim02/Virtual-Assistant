import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, RTCConfiguration
import numpy as np
import av
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

st.title("Ansari Voice Assistant (webrtc live mic POC)")

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class ASRProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.buffer = bytes()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert frame to raw audio bytes
        array = frame.to_ndarray()  # shape (channels, samples)
        # flatten to mono if needed
        if array.ndim > 1:
            array = array.mean(axis=0).astype(np.int16)
        else:
            array = array.astype(np.int16)
        # Feed some audio to speech_recognition from temporary file (short chunks)
        # We'll write to temp WAV and run recognize on small segments
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        # Use av to write WAV? Simpler: use soundfile if available. As a minimal example we write raw PCM not handled well here.
        # For a robust solution use soundfile or sox utilities. This is a minimal illustrative snippet.
        try:
            import soundfile as sf
            sf.write(tmp.name, array, frame.sample_rate, subtype='PCM_16')
            with sr.AudioFile(tmp.name) as source:
                audio = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio)
                    # send TTS: create file and use Streamlit callback to show later
                    st.session_state['last_text'] = text
                except Exception:
                    pass
        except Exception as e:
            print("Write/ASR error:", e)
        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

        return frame

webrtc_ctx = webrtc_streamer(
    key="ansari",
    mode="SENDRECV",
    rtc_configuration=RTC_CONFIGURATION,
    audio_processor_factory=ASRProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# Display last recognized text
if 'last_text' in st.session_state:
    st.write("Last recognized:", st.session_state['last_text'])
