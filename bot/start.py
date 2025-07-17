from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import COOLDOWN_SECONDS, REFERRAL_BONUS_LIMIT
from bot import database as db
from bot.media import get_random_media
from bot.utils import format_seconds, is_on_cooldown, is_bonus_active
from bot.referral import (
    track_referral,
    get_user_referrals,
    should_activate_bonus,
    apply_referral_bonus
)
import time


@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    mention = message.from_user.mention(style="markdown")

    # ✅ Track referral if provided
    referred_by = None
    if len(message.command) > 1 and message.command[1].startswith("ref="):
        try:
            referred_by = int(message.command[1].split("ref=")[1])
            await track_referral(user_id, referred_by)
        except Exception as e:
            print(f"[REFERRAL] Error: {e}")
            await db.create_or_update_user(user_id)
    else:
        await db.create_or_update_user(user_id)

    # ✅ Force-subscription check
    fsub_channel = await db.get_setting("force_sub_channel")
    if fsub_channel:
        try:
            member = await client.get_chat_member(fsub_channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                raise Exception("Not a member")
        except:
            join_url = f"https://t.me/c/{str(fsub_channel)[4:]}" if str(fsub_channel).startswith("-100") else f"https://t.me/{fsub_channel}"
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔔 Join Channel", url=join_url)],
                [InlineKeyboardButton("✅ I've Joined", url=f"https://t.me/{client.me.username}?start=start")]
            ])
            return await message.reply(
                f"🚫 Hello {mention}, you need to join our channel to use this bot.",
                reply_markup=join_button
            )

    # ✅ Cooldown & bonus logic
    user = await db.get_user(user_id)
    now = int(time.time())
    last_drop = user.get("last_media_time", 0)
    bonus_expiry = user.get("bonus_expiry", 0)
    is_bonus = is_bonus_active(bonus_expiry)
    cooldown_remaining = is_on_cooldown(last_drop, COOLDOWN_SECONDS)
    can_send = is_bonus or cooldown_remaining == 0

    # ✅ Send media if allowed
    if can_send:
        media = await get_random_media()
        if not media:
            return await message.reply("⚠️ Media pool is empty. Please ask the admin to run /setmedia.")
        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=media["chat_id"],
                message_id=media["message_id"]
            )
            await db.update_last_media_time(user_id, now)
        except:
            return await message.reply("❌ Failed to send media. Please try again later.")
    else:
        return await message.reply(f"🕒 You need to wait `{format_seconds(cooldown_remaining)}` before receiving more content.")

    # ✅ Referrals & bonus reward
    referral_count = await get_user_referrals(user_id)
    if should_activate_bonus(referral_count) and not is_bonus:
        await apply_referral_bonus(user_id)
        is_bonus = True

    referrals_left = max(0, REFERRAL_BONUS_LIMIT - referral_count)
    share_link = f"https://t.me/{client.me.username}?start=ref={user_id}"
    bonus_status = "🟢 Active" if is_bonus else "🔴 Inactive"

    text = (
        f"👋 Hello {mention}!\n\n"
        f"🎉 You received your reward!\n"
        f"👥 Referrals: `{referral_count}`\n"
        f"🎯 Referral Goal: `{REFERRAL_BONUS_LIMIT}`\n"
        f"🎁 Bonus Access: `{bonus_status}`\n\n"
        f"✨ Invite your friends to unlock more content!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 Invite Friends", url=f"https://t.me/share/url?url={share_link}")],
        [InlineKeyboardButton("💼 My Stats", url=f"https://t.me/{client.me.username}?start=start")]
    ])

    await message.reply(text, reply_markup=keyboard)
