from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import traceback
import time
import json
from datetime import datetime
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

# Enhanced memory: Store multiple conversations with metadata
conversations = {}
chat_metadata = {}

# Frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

def generate_chat_id():
    """Generate unique chat ID"""
    return f"chat_{int(time.time())}"

def save_chat_to_file(chat_id, conversation):
    """Save chat to JSON file for persistence"""
    try:
        os.makedirs("chat_history", exist_ok=True)
        with open(f"chat_history/{chat_id}.json", "w") as f:
            json.dump({
                "chat_id": chat_id,
                "conversation": conversation,
                "metadata": chat_metadata.get(chat_id, {}),
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving chat: {e}")

def load_chat_from_file(chat_id):
    """Load chat from JSON file"""
    try:
        with open(f"chat_history/{chat_id}.json", "r") as f:
            data = json.load(f)
            return data.get("conversation", []), data.get("metadata", {})
    except:
        return None, None

def load_all_chats():
    """Load all available chats"""
    chats = []
    try:
        if os.path.exists("chat_history"):
            for filename in os.listdir("chat_history"):
                if filename.endswith(".json"):
                    chat_id = filename[:-5]  # Remove .json extension
                    try:
                        with open(f"chat_history/{filename}", "r") as f:
                            data = json.load(f)
                            # Get first user message as title, or use timestamp
                            title = "New Chat"
                            for msg in data.get("conversation", []):
                                if msg.get("role") == "user":
                                    title = msg.get("content", "")[:50] + ("..." if len(msg.get("content", "")) > 50 else "")
                                    break

                            chats.append({
                                "chat_id": chat_id,
                                "title": title,
                                "last_updated": data.get("last_updated", ""),
                                "message_count": len([m for m in data.get("conversation", []) if m.get("role") != "system"])
                            })
                    except:
                        continue
    except Exception as e:
        print(f"Error loading chats: {e}")

    # Sort by last updated
    chats.sort(key=lambda x: x["last_updated"], reverse=True)
    return chats

@app.route("/api/chats", methods=["GET"])
def get_all_chats():
    """Get list of all available chats"""
    chats = load_all_chats()
    return jsonify({"chats": chats})

@app.route("/api/chat/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    """Get specific chat history"""
    if chat_id in conversations:
        # Chat is in memory
        messages = [msg for msg in conversations[chat_id] if msg["role"] != "system"]
        return jsonify({
            "chat_id": chat_id,
            "messages": messages,
            "metadata": chat_metadata.get(chat_id, {})
        })
    else:
        # Try to load from file
        conversation, metadata = load_chat_from_file(chat_id)
        if conversation:
            # Load into memory
            conversations[chat_id] = conversation
            chat_metadata[chat_id] = metadata or {}
            messages = [msg for msg in conversation if msg["role"] != "system"]
            return jsonify({
                "chat_id": chat_id,
                "messages": messages,
                "metadata": metadata or {}
            })

    return jsonify({"error": "Chat not found"}), 404

@app.route("/api/chat/new", methods=["POST"])
def create_new_chat():
    """Create a new chat"""
    chat_id = generate_chat_id()
    conversations[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat_metadata[chat_id] = {
        "created": datetime.now().isoformat(),
        "title": "New Chat"
    }
    return jsonify({"chat_id": chat_id})

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    chat_id = data.get("chat_id")
    user_message = data.get("message", "")

    if not chat_id:
        # Create new chat if none provided
        chat_id = generate_chat_id()
        conversations[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat_metadata[chat_id] = {
            "created": datetime.now().isoformat(),
            "title": user_message[:50] + ("..." if len(user_message) > 50 else "")
        }

    if not user_message:
        return jsonify({"error": "No message sent"}), 400

    # Load chat if not in memory
    if chat_id not in conversations:
        conversation, metadata = load_chat_from_file(chat_id)
        if conversation:
            conversations[chat_id] = conversation
            chat_metadata[chat_id] = metadata or {}
        else:
            conversations[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
            chat_metadata[chat_id] = {"created": datetime.now().isoformat()}

    # Add user message
    conversations[chat_id].append({"role": "user", "content": user_message})

    # Update title if this is first message
    if chat_metadata[chat_id].get("title") == "New Chat":
        chat_metadata[chat_id]["title"] = user_message[:50] + ("..." if len(user_message) > 50 else "")

    payload = {
        "model": MODEL_NAME,
        "messages": conversations[chat_id],
        "temperature": 0.5
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Try to get AI response
    for attempt in range(3):
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            res.raise_for_status()
            ai_reply = res.json()["choices"][0]["message"]["content"]
            conversations[chat_id].append({"role": "assistant", "content": ai_reply})

            # Save to file
            save_chat_to_file(chat_id, conversations[chat_id])

            return jsonify({
                "response": ai_reply,
                "chat_id": chat_id
            })

        except requests.exceptions.HTTPError as e:
            if res.status_code == 503 and attempt < 2:
                time.sleep(2)
                continue
            print(f"HTTPError from Groq: {e}")
            return jsonify({"error": "HAL is currently unavailable."}), 503
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "HAL encountered an error."}), 503

    return jsonify({"error": "HAL is offline."}), 503

@app.route("/api/chat/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    """Delete a chat"""
    # Remove from memory
    conversations.pop(chat_id, None)
    chat_metadata.pop(chat_id, None)

    # Remove file
    try:
        if os.path.exists(f"chat_history/{chat_id}.json"):
            os.remove(f"chat_history/{chat_id}.json")
    except Exception as e:
        print(f"Error deleting chat file: {e}")

    return jsonify({"status": "deleted"})

@app.route("/api/chat/<chat_id>/rename", methods=["POST"])
def rename_chat(chat_id):
    """Rename a chat"""
    data = request.get_json()
    new_title = data.get("title", "").strip()

    if not new_title:
        return jsonify({"error": "Title cannot be empty"}), 400

    if chat_id in chat_metadata:
        chat_metadata[chat_id]["title"] = new_title
        # Save updated metadata
        if chat_id in conversations:
            save_chat_to_file(chat_id, conversations[chat_id])
        return jsonify({"status": "renamed", "title": new_title})

    return jsonify({"error": "Chat not found"}), 404

# Serve frontend files
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-store"
    return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
