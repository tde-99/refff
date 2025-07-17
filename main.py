from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from bot import start, media, settings_panel  # Only import req_fsub if it exists

app = Client(
    "referral_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 🔍 DEBUG: Log all incoming messages
@app.on_message(filters.all)
async def debug_logger(client, message):
    print(f"[DEBUG] Received message: {message.text} from {message.from_user.id}")

if __name__ == "__main__":
    print("🤖 Bot is starting...")
    app.run()
