import os
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "insert_your_elevenlabs_api_key_here")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "insert_your_elevenlabs_voice_id_here")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "groq_api_key_here")
MODEL_NAME = os.getenv("MODEL_NAME", "groq_model_name_here")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "insert_your_system_prompt_here")
