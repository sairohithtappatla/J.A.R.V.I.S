# tts/tts.py
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)      # Speed
    engine.setProperty('volume', 1.0)    # Volume (0.0 to 1.0)

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 0 = default voice

    engine.say(text)
    engine.runAndWait()
