import os
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "insert_your_elevenlabs_api_key_here")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "insert_your_elevenlabs_voice_id_here")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "groq_api_key_here")
MODEL_NAME = os.getenv("MODEL_NAME", "groq_model_name_here")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "insert_your_system_prompt_here")
FONT = ("Helvetica", 14)
BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
CHAT_BG_COLOR = "#2e2e2e"
def validate_config():
    if not ELEVEN_API_KEY or ELEVEN_API_KEY == "insert_your_elevenlabs_api_key_here":
        raise ValueError("Please set your ElevenLabs API key in the .env file.")
    if not ELEVEN_VOICE_ID or ELEVEN_VOICE_ID == "insert_your_elevenlabs_voice_id_here":
        raise ValueError("Please set your ElevenLabs voice ID in the .env file.")
    if not GROQ_API_KEY or GROQ_API_KEY == "groq_api_key_here":
        raise ValueError("Please set your Groq API key in the .env file.")
    if not MODEL_NAME or MODEL_NAME == "groq_model_name_here":
        raise ValueError("Please set your Groq model name in the .env file.")
    if not SYSTEM_PROMPT or SYSTEM_PROMPT == "insert_your_system_prompt_here":
        raise ValueError("Please set your system prompt in the .env file.")
validate_config()