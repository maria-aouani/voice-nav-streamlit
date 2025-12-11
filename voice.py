# voice.py
import os
import platform
from gtts import gTTS
import speech_recognition as sr
import streamlit as st
from io import BytesIO

def speak(text):
    """
    Speak text out loud.
    Locally uses playsound, in Streamlit deployment uses st.audio.
    """
    tts = gTTS(text=text, lang="en")
    filename = "voice_output.mp3"
    tts.save(filename)

    if platform.system() == "Windows":
        # Local Windows environment
        try:
            from playsound import playsound
            playsound(filename)
        except Exception as e:
            print(f"Audio playback error: {e}")
    else:
        # Streamlit Cloud / Linux
        try:
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except Exception as e:
            st.error(f"Audio playback error: {e}")

    # Remove file
    if os.path.exists(filename):
        os.remove(filename)

# Alias for English speech
speak_eng = speak

def listen():
    """
    Listen to microphone and return recognized text.
    Works only locally (Windows/macOS/Linux with mic).
    """
    if platform.system() != "Windows" and not hasattr(sr, "Microphone"):
        st.warning("Voice recognition works only locally with a microphone.")
        return ""

    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="en-EN")
        return text
    except sr.UnknownValueError:
        return "Couldn't recognize."
    except sr.RequestError:
        return "Speech recognition service error."
