import logging
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN

# Enable logging
logging.basicConfig(level=logging.INFO)

app = Client(
    "referral_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Import and register handlers
from bot import start, media, settings_panel, req_fsub

if __name__ == "__main__":
    print("🤖 Bot is starting...")
    app.run()
