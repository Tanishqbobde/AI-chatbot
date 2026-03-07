import os
from flask import Flask, request, jsonify, send_from_directory, session
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# -------------------------------
# System Prompt
# -------------------------------

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are a smart AI assistant inside a website.
Be helpful, clear, and conversational.
Give short and structured answers when possible.
Avoid unnecessary symbols and respond professionally.
"""
}

# -------------------------------
# Home Page
# -------------------------------

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


# -------------------------------
# Chat Endpoint
# -------------------------------

@app.route('/chat', methods=['POST'])
def chat():
    try:

        data = request.get_json()
        user_message = data.get("message", "")

        print(f"[USER] {user_message}")

        # Initialize session history
        if "history" not in session:
            session["history"] = [SYSTEM_PROMPT]

        history = session["history"]

        # Add user message
        history.append({
            "role": "user",
            "content": user_message
        })

        # Send history to Groq
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=history,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        reply = completion.choices[0].message.content

        print(f"[BOT] {reply}")

        # Save bot reply
        history.append({
            "role": "assistant",
            "content": reply
        })

        session["history"] = history

        return jsonify({
            "reply": reply,
            "history_length": len(history)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "error": str(e)
        }), 500


# -------------------------------
# Clear Chat
# -------------------------------

@app.route('/clear', methods=['POST'])
def clear_chat():
    session.pop("history", None)
    return jsonify({"status": "chat cleared"})


# -------------------------------
# Run App
# -------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)