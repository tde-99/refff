import time
from config import REFERRAL_BONUS_LIMIT, ACCESS_TIME_LIMIT
from bot import database as db


# ✅ Log referral if valid (not self-referral)
async def track_referral(user_id: int, referrer_id: int):
    if user_id == referrer_id:
        return  # Self-referral not allowed

    existing_user = await db.get_user(user_id)
    if not existing_user:
        await db.create_or_update_user(user_id, referrer_id)
        await db.add_referral(referrer_id, user_id)


# ✅ Get total referrals for a user
async def get_user_referrals(user_id: int) -> int:
    user = await db.get_user(user_id)
    return len(user.get("referrals", [])) if user else 0


# ✅ Determine if user qualifies for bonus
def should_activate_bonus(ref_count: int) -> bool:
    return ref_count >= REFERRAL_BONUS_LIMIT


# ✅ Apply bonus to user
async def apply_referral_bonus(user_id: int):
    expiry_time = int(time.time()) + ACCESS_TIME_LIMIT
    await db.set_bonus_expiry(user_id, expiry_time)
