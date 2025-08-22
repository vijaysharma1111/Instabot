import os
import requests
import yt_dlp
from flask import Flask, request

app = Flask(__name__)

# ---------------- CONFIG ----------------
BOT_TOKEN = "7657125691:AAFm8yyWeB8Y-R12eHVhp-r6Kgr6Qs7g8nY"
FORCE_CHANNEL = "@freeultraapk"
WEBHOOK_URL = "https://instaytbot-3.onrender.com/webhook"

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
        ydl_opts = {
            "format": "mp4",
            "outtmpl": "video.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print("Download error:", e)
        return None

# --------- HANDLE UPDATES ----------
def handle_update(data):
    if "message" not in data:
        return

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    if "text" not in msg:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Sirf video link bhejo!"
        })
        return

    text = msg["text"]

    # /start command
    if text == "/start":
        if not is_subscribed(chat_id):
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👉 Pehle channel join karo: {FORCE_CHANNEL}"
            })
        else:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "👋 Mujhe YouTube/Instagram link bhejo, mai video bhej dunga 🚀"
            })
        return

    # Force Join Check
    if not is_subscribed(chat_id):
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"👉 Pehle channel join karo: {FORCE_CHANNEL}"
        })
        return

    # Agar user ne link bheja
    if "http" in text:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⏳ Download ho raha hai..."
        })

        file_path = download_video(text)

        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                requests.post(
                    f"{API_URL}/sendVideo",
                    data={"chat_id": chat_id},
                    files={"video": f},
                )
            os.remove(file_path)
        else:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ Video download fail ho gaya."
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
    set_hook = f"{API_URL}/setWebhook?url={WEBHOOK_URL}"
    requests.get(set_hook)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
