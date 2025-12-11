import os
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

def speak(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice_output.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

def speak_eng(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice_output.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="en-EN")
        return text
    except:
        return "Couldn't recognize."
