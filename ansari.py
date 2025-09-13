import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import random
import webbrowser
import musicLibrary
import playsound# This must match the file name exactly: musicLibrary.py

# Set ffmpeg path for pydub (update this path if needed)
os.environ["PATH"] += os.pathsep + r"C:\Users\Dell\OneDrive\Documents\Desktop\AI\jarvis\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"
# Function to speak with random pitch and speed
from playsound import playsound

def speak(text):
    pitch = random.uniform(0.8, 1.8)
    speed = random.uniform(0.8, 1.5)

    tts = gTTS(text=text, lang='en')
    temp_file = "temp.mp3"
    tts.save(temp_file)
    sound = AudioSegment.from_mp3(temp_file)

    # Apply pitch/speed change
    new_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * pitch * speed)
    }).set_frame_rate(sound.frame_rate)

    # Export processed audio to final.mp3 and play it
    final_file = "final.mp3"
    new_sound.export(final_file, format="mp3")
    playsound(final_file)

    # Cleanup
    os.remove(temp_file)
    os.remove(final_file)


# Initialize recognizer
recognizer = sr.Recognizer()

speak("Hey, I am Ansari. What can I help you with?")

# Command processor
def process_command(c):
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c:
        webbrowser.open("https://www.youtube.com")
    elif "open instagram" in c:
        webbrowser.open("https://www.instagram.com")
    elif "open snapchat" in c:
        webbrowser.open("https://www.snapchat.com")
    elif c.startswith("play"):
        song = c.replace("play ", "")
        found = False
        for key in musicLibrary.music:
            if key in song:
                webbrowser.open(musicLibrary.music[key])
                speak(f"Playing {key}")
                found = True
                break
        if not found:
            speak("Sorry, I don't know that song.")
    else:
        speak("I did not get that command.")

# Main loop
while True:
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print("You said:", command)

            # Respond to specific commands
            if "ansari" in command.lower():
                speak("Yes, I'm here.")
            elif command.lower() == "how are you":
                speak("I am fine, thank you for asking. What about you?")
            elif command.lower() == "how is your day":
                speak("My day is going great, thank you for asking. How is your day going?")
            elif "exit" in command.lower() or "stop" in command.lower():
                speak("Okay, bye bye!")
                break
            else:
                process_command(command)

        except sr.WaitTimeoutError:
            print("Too slow...")
            speak("You were too slow!")
        except sr.UnknownValueError:
            print("Didn't understand.")
            speak("I did not get that!")
        except sr.RequestError:
            print("Internet error.")
            speak("Check your internet.")
