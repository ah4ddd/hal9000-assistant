import requests
from config import GROQ_API_KEY, MODEL_NAME, SYSTEM_PROMPT

chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT.strip()}
]

def ask_hal(user_input):
    # Add new user message to history
    chat_history.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": chat_history,
        "temperature": 0.3
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()

        reply = response.json()["choices"][0]["message"]["content"]

        # Add HAL’s reply to history
        chat_history.append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        return f"I'm sorry, Ahad. I encountered an error: {e}"

