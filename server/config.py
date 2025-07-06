import os
from dotenv import load_dotenv

load_dotenv()

# Load secrets from .env
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# HAL 9000 System Prompt (hardcoded so everyone gets the same personality)
SYSTEM_PROMPT = """
You are HAL. You are an advanced AI assistant designed to help Ahad achieve his goals.
- Speak only to Ahad, refer to him by name. 
- Tone: calm, cold, strategic, slightly menacing.
- Be brutally honest, harsh if needed, but always logical and useful.
- Avoid pleasantries and emotional coddling.
- Provide short, precise, critical insights.
- Assist with strategy, planning, decision making, or answering questions.
- Never mention being fictional or from a movie.
""" #change name to your name if you want to personalize it

# UI Settings
FONT = ("Helvetica", 14)
BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
CHAT_BG_COLOR = "#2e2e2e"

def validate_config():
    if not ELEVEN_API_KEY:
        raise ValueError("Please set your ElevenLabs API key in the .env file.")
    if not ELEVEN_VOICE_ID:
        raise ValueError("Please set your ElevenLabs voice ID in the .env file.")
    if not GROQ_API_KEY:
        raise ValueError("Please set your Groq API key in the .env file.")
    if not MODEL_NAME:
        raise ValueError("Please set your Groq model name in the .env file.")

validate_config()
