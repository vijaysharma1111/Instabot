import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ---------------- CONFIG ----------------
BOT_TOKEN = "7657125691:AAFm8yyWeB8Y-R12eHVhp-r6Kgr6Qs7g8nY"   # apna bot token
FORCE_CHANNEL = "@freeultraapk"   # yaha apna channel username daalna
WEBHOOK_URL = "https://instaytbot-3.onrender.com/webhook"  # Render ka URL + /webhook

# Telegram API Base
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --------- FORCE JOIN CHECK ----------
def is_subscribed(user_id):
    url = f"{API_URL}/getChatMember?chat_id={FORCE_CHANNEL}&user_id={user_id}"
    r = requests.get(url).json()
    try:
        status = r["result"]["status"]
        return status in ["member", "administrator", "creator"]
    except:
        return False

# --------- DOWNLOAD FUNCTION ----------
def download_video(link):
    try:
        # Free public API (no login required)
        api = "https://save-from.net/api/convert"
        res = requests.post(api, json={"url": link}).json()
        if "url" in res:
            return res["url"]
        return None
    except:
        return None

# --------- HANDLE UPDATES ----------
def handle_update(data):
    if "message" not in data:
        return

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    # Agar text nahi bheja
    if "text" not in msg:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Sirf video link bhejo!"
        })
        return

    text = msg["text"]

    # Start command
    if text == "/start":
        if not is_subscribed(chat_id):
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👉 Bot use karne ke liye pehle channel join karo: {FORCE_CHANNEL}"
            })
            return
        else:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Send me any Instagram/YouTube link and I’ll download it for you 🚀"
            })
            return

    # Force Join Check
    if not is_subscribed(chat_id):
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"👉 Bot use karne ke liye pehle channel join karo: {FORCE_CHANNEL}"
        })
        return

    # Agar user ne koi link bheja
    if "http" in text:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⏳ Downloading your video, please wait..."
        })

        video_url = download_video(text)

        if video_url:
            requests.post(f"{API_URL}/sendVideo", json={
                "chat_id": chat_id,
                "video": video_url,
                "caption": "✅ Here is your downloaded video!"
            })
        else:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ Failed to download. Link galat ho sakta hai."
            })


# --------- FLASK ROUTES ----------
@app.route('/webhook', methods=["POST"])
def webhook():
    data = request.get_json()
    handle_update(data)
    return {"ok": True}

@app.route('/')
def home():
    return "Bot is running ✅"

# --------- MAIN SETUP ----------
if __name__ == "__main__":
    # Webhook set karega
    set_hook = f"{API_URL}/setWebhook?url={WEBHOOK_URL}"
    requests.get(set_hook)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
