# 🎙️ Voice Assistant using Python (Speech Recognition & Text-to-Speech)

## Problem Statement
Interacting with a computer using keyboard and mouse is not always convenient.  
The goal of this project is to build a **simple voice-controlled assistant** that can:
- listen to spoken commands,
- understand basic user intent,
- respond using voice,
- and perform simple tasks like opening websites or playing music.

---

## What This Project Does
This project implements a **Python-based voice assistant** that listens through the microphone, converts speech to text, processes commands, and responds using speech.

In simple terms:
- You speak a command
- The system listens and understands it
- It performs an action (open Google, play music, etc.)
- It replies back using voice

---

## Features
- 🎧 Real-time voice input using microphone  
- 🗣️ Speech-to-text using Google Speech Recognition  
- 🔊 Text-to-speech responses using gTTS  
- 🎶 Plays songs from a custom music library  
- 🌐 Opens websites like Google, YouTube, Instagram, Snapchat  
- 🎛️ Randomized voice pitch and speed for natural sound  
- ❌ Graceful exit using voice commands  

---

## How the System Works (Step-by-Step)

### 1️⃣ Speech Recognition
- Uses the `speech_recognition` library
- Captures audio from the microphone
- Converts spoken words into text using Google’s speech API

---

### 2️⃣ Command Processing
The recognized text is converted to lowercase and matched against predefined commands such as:
- `open google`
- `open youtube`
- `play <song name>`
- `exit` or `stop`

Each command triggers a specific action.

---

### 3️⃣ Text-to-Speech Response
- Uses `gTTS` (Google Text-to-Speech)
- Audio is temporarily generated as an MP3 file
- `pydub` is used to modify pitch and speed
- The response is played back using `playsound`

---

### 4️⃣ Music Playback
- Songs are stored as links inside `musicLibrary.py`
- When a user says `play <song name>`, the assistant opens the corresponding URL in the browser

---

## Tech Stack
- **Language:** Python  
- **Libraries Used:**
  - speech_recognition  
  - gTTS  
  - pydub  
  - playsound  
  - webbrowser  

---

## Project Structure
