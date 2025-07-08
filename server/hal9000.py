from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import traceback
from dotenv import load_dotenv

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load .env
load_dotenv()

# Get env variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

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

# ✅ Absolute path to frontend folder (WORKS LOCALLY AND ON RENDER)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
print("Frontend directory resolved to:", FRONTEND_DIR)

# ✅ API endpoint
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

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        res.raise_for_status()
        ai_reply = res.json()["choices"][0]["message"]["content"]
        conversations[user_id].append({"role": "assistant", "content": ai_reply})
        return jsonify({"response": ai_reply})
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to get response from AI"}), 500

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
