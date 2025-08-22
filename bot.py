import telebot
from flask import Flask, request
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")  # Render pe environment variable me daalo
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Bot is running!", 200

# Telegram webhook listener
@app.route(f"/{TOKEN}", methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Send me an Instagram video link and I'll try to download it.")

# Handle links
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(message, "⚠️ Please send a valid Instagram link.")
        return

    try:
        ydl_opts = {
            "outtmpl": "video.mp4",
            "format": "best",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        with open("video.mp4", "rb") as f:
            bot.send_video(message.chat.id, f)

        os.remove("video.mp4")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
