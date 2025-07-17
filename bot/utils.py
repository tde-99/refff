import time


# ⏳ Format seconds into HH:MM:SS or Xm Ys
def format_seconds(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    elif minutes:
        return f"{minutes}m {sec}s"
    else:
        return f"{sec}s"


# ⏱️ Check if user is in cooldown
def is_on_cooldown(last_time: int, cooldown: int) -> int:
    now = int(time.time())
    elapsed = now - last_time
    remaining = cooldown - elapsed
    return max(0, remaining)


# 🎁 Check if referral bonus is active
def is_bonus_active(bonus_expiry: int) -> bool:
    return int(time.time()) < bonus_expiry
