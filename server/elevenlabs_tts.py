import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume 0.0 to 1.0

def speak_hal(text):
    print(f"[HAL 9000]: {text}")
    engine.say(text)
    engine.runAndWait()
