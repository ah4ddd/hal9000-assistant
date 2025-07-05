import requests
import os
import tempfile
import playsound
from config import ELEVEN_API_KEY, ELEVEN_VOICE_ID

def speak_hal(text):
    print(f"[HAL 9000]: {text}")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"[ERROR]: ElevenLabs returned {response.status_code}")
        print(response.text)
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
        f.write(response.content)
        audio_file = f.name

    playsound.playsound(audio_file)
    os.remove(audio_file)
