from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import traceback
import time
from dotenv import load_dotenv

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load .env
load_dotenv()

# Get env variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# Debug: Print what we loaded
print(f"DEBUG - Loaded API Key: {GROQ_API_KEY[:20]}..." if GROQ_API_KEY else "NO API KEY")
print(f"DEBUG - Loaded Model: {MODEL_NAME}")

# Define system prompt
SYSTEM_PROMPT = """
You are HAL. You are an advanced AI assistant designed to help Ahad achieve his goals.
- Speak only to Ahad, refer to him by name.
- Tone: calm, cold, strategic, slightly menacing.
- Be brutally honest, harsh if needed, but always logical and useful.
- Avoid pleasantries and emotional coddling.
- Provide short, precise, critical insights.
- Assist with strategy, planning, decision making, or answering questions.
- Never mention being fictional or from a movie.
"""

# Memory: in-memory store
conversations = {}

# ✅ Absolute path to frontend folder
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
print("Frontend directory resolved to:", FRONTEND_DIR)

# ✅ API endpoint for asking HAL

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    print("REQUEST RECEIVED from:", request.remote_addr)

    if not user_message:
        return jsonify({"error": "No message sent"}), 400

    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    conversations[user_id].append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_NAME,
        "messages": conversations[user_id],
        "temperature": 0.5
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # DEBUG: Print what we're sending
    print(f"DEBUG - Sending payload: {payload}")

    # --- Retry logic with 3 attempts ---
    for attempt in range(3):
        try:
            print(f"Calling Groq API (attempt {attempt + 1})")
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            # DEBUG: Print response details
            print(f"DEBUG - Response Status: {res.status_code}")
            print(f"DEBUG - Response Headers: {dict(res.headers)}")
            print(f"DEBUG - Response Body: {res.text}")

            res.raise_for_status()
            ai_reply = res.json()["choices"][0]["message"]["content"]
            conversations[user_id].append({"role": "assistant", "content": ai_reply})
            return jsonify({"response": ai_reply})

        except requests.exceptions.HTTPError as e:
            if res.status_code == 503 and attempt < 2:
                print("Groq returned 503, retrying in 2 seconds...")
                time.sleep(2)
                continue
            print("HTTPError from Groq:", e)
            print(f"DEBUG - Error Response: {res.text}")  # This will show us what Groq says
            traceback.print_exc()
            return jsonify({"error": "HAL is currently unavailable. Please try again later."}), 503

        except requests.exceptions.RequestException as e:
            print("RequestException calling Groq:", e)
            traceback.print_exc()
            return jsonify({"error": "HAL encountered a network error."}), 503

    # --- Fallback if all retries fail ---
    return jsonify({"error": "HAL is currently offline. Try again later."}), 503


# ✅ New endpoint to reset conversation
@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json()
    user_id = data.get("user_id", "default")
    conversations.pop(user_id, None)
    print(f"Conversation reset for user: {user_id}")
    return jsonify({"status": "reset"})


# ✅ Serve index.html at /
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

# ✅ Serve static files
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# ✅ Disable caching
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-store"
    return r

# ✅ Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
