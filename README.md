<p align="center">
  <img src="hal-banner.png" alt="HAL 9000 Assistant Banner" width="100%" />
</p>

# HAL 9000 Assistant

An unfiltered, strategic personal AI — built to **think**, not please.  
Still in its early stage, still evolving — but even now, it cuts through noise like a blade.

---

### 🧠 What Is This?

A base model for a ruthless AI assistant, HAL is designed to:
- Be brutally honest and coldly strategic
- Store per-user context (ephemeral for now)
- Serve responses via Groq’s blazing-fast LLaMA models
- Be extended, repurposed, or rebranded by anyone

If you're looking for sugarcoated answers or polite small talk, you're in the wrong repo.

---

### 🧬 Tech Stack

| Language    | %      |
|-------------|--------|
| Python      | 51.9%  |
| JavaScript  | 25.3%  |
| CSS         | 16.4%  |
| HTML        | 6.4%   |

- **Backend**: Flask
- **Frontend**: Vanilla JS, HTML, CSS (minimal and raw)
- **AI**: Groq API using `llama3-8b-8192`
- **Memory**: In-memory per user session (stateless reset included)

---

### ⚙️ Key Features

- **System Prompt** crafted for maximum edge and focus  
- **User Memory** stored per session, with easy `/reset` option  
- **Retry mechanism** for Groq API fails (no weak links)  
- **Simple frontend** that gets out of your way  
- **CORS enabled** for full-stack flexibility

---

### 🧩 Usage

Already hosted and running.  
But if you're forking it or customizing:

- Update `.env` with your Groq API key
- Edit the `SYSTEM_PROMPT` in `app.py` to match your vision
- Drop any frontend changes in the `frontend/` folder — backend serves it automatically

---

### 🔥 Customize It

Make your own version:
- Change the name
- Replace the tone
- Extend memory, auth, storage, even add a voice layer

This is the **base model**. A skeleton with attitude. Build on it. Break it. Push it further.

---

### 🧼 No Bullshit License

Use it. Remix it. Sell it. Credit optional.  
Just don’t make it lame.

---

### 👨‍🚀 Status: Pre-Beta / Actively Building

HAL is **not done**. This is just the beginning.  
More features, memory persistence, auth, maybe even a proper frontend — coming when it’s time. Not rushed. Not bloated. Not for show.

---

### Author

I built this for myself. If it helps you — good.  
If not — build your own. Created by Ahad [`ah4ddd`](https://github.com/ah4ddd)
---
