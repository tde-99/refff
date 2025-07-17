import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI")

MEDIA_CHANNEL_ID = int(os.getenv("MEDIA_CHANNEL_ID"))

# Defaults / fallback values (can be overwritten via admin commands)
START_MEDIA_COUNT = int(os.getenv("START_MEDIA_COUNT", 1))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 3600))
REFERRAL_BONUS_LIMIT = int(os.getenv("REFERRAL_BONUS_LIMIT", 3))
ACCESS_TIME_LIMIT = int(os.getenv("ACCESS_TIME_LIMIT", 86400))  # 24h

STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"

admins_env = os.getenv("ADMINS")
if not admins_env:
    print("⚠️ ADMINS environment variable not set. Some features may be restricted.")
    ADMINS = []
else:
    try:
        ADMINS = list(map(int, admins_env.split()))
    except ValueError:
        print("❌ Invalid ADMINS environment variable. Please provide a space-separated list of user IDs.")
        ADMINS = []
