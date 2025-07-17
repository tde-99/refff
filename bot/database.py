from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["referral_bot_db"]


# --------------------------
# SETTINGS
# --------------------------

async def set_setting(key: str, value):
    await db["settings"].update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

async def get_setting(key: str):
    result = await db["settings"].find_one({"key": key})
    return result["value"] if result else None


# --------------------------
# USERS & REFERRALS
# --------------------------

async def create_or_update_user(user_id: int, referred_by: int = None):
    existing = await db["users"].find_one({"user_id": user_id})
    if not existing:
        await db["users"].insert_one({
            "user_id": user_id,
            "referred_by": referred_by,
            "referrals": [],
            "last_media_time": 0,
            "bonus_expiry": 0
        })

async def get_user(user_id: int):
    return await db["users"].find_one({"user_id": user_id})

async def add_referral(referrer_id: int, new_user_id: int):
    await db["users"].update_one({"user_id": referrer_id}, {"$addToSet": {"referrals": new_user_id}})

async def update_last_media_time(user_id: int, timestamp: int):
    await db["users"].update_one({"user_id": user_id}, {"$set": {"last_media_time": timestamp}})

async def set_bonus_expiry(user_id: int, expiry: int):
    await db["users"].update_one({"user_id": user_id}, {"$set": {"bonus_expiry": expiry}})

async def get_all_users():
    return db["users"].find()

async def count_total_referrals():
    return await db["users"].count_documents({"referred_by": {"$ne": None}})


# --------------------------
# MEDIA POOL
# --------------------------

async def save_media_to_pool(
    chat_id: int,
    message_id: int,
    media_type: str,
    caption: str,
    custom_caption: str = None,
    button_text: str = None,
    button_url: str = None
):
    existing = await db["media_pool"].find_one({
        "chat_id": chat_id,
        "message_id": message_id
    })
    if existing:
        return False
    await db["media_pool"].insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "media_type": media_type,
        "caption": caption,
        "custom_caption": custom_caption,
        "button_text": button_text,
        "button_url": button_url
    })
    return True

async def get_all_media():
    return await db["media_pool"].find().to_list(length=None)


# --------------------------
# FORCE-SUB JOIN REQUEST TRACKING
# --------------------------

async def add_req_channel(chat_id: int):
    await db["req_channels"].update_one({"chat_id": chat_id}, {"$set": {}}, upsert=True)

async def reqChannel_exist(chat_id: int):
    return await db["req_channels"].find_one({"chat_id": chat_id}) is not None

async def reqSent_user(chat_id: int, user_id: int):
    await db["req_sent_users"].update_one(
        {"chat_id": chat_id, "user_id": user_id}, {"$set": {}}, upsert=True
    )

async def reqSent_user_exist(chat_id: int, user_id: int):
    return await db["req_sent_users"].find_one({"chat_id": chat_id, "user_id": user_id}) is not None

async def del_reqSent_user(chat_id: int, user_id: int):
    await db["req_sent_users"].delete_one({"chat_id": chat_id, "user_id": user_id})
