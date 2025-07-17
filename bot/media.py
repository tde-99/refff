from main import app
import random
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message
from config import ADMINS, MEDIA_CHANNEL_ID
from bot import database as db


# 🎞️ /setmedia — Admin-only: Index media from your channel into the pool
@app.on_message(filters.command("setmedia"))
async def set_media_pool(client: Client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to use this command.")

    await message.reply("📥 Indexing media from the channel...\n\nThis may take a few seconds...")
    saved, skipped, total = 0, 0, 0

    try:
        # Check if bot is admin in the channel
        try:
            chat = await client.get_chat(MEDIA_CHANNEL_ID)
            me = await chat.get_member((await client.get_me()).id)
            if me.status not in ["administrator", "creator"]:
                return await message.reply(f"❌ I am not an admin in the media channel: `{MEDIA_CHANNEL_ID}`")
        except Exception as e:
            return await message.reply(f"❌ Error checking admin status in media channel: `{e}`")

        async for msg in client.iter_messages(MEDIA_CHANNEL_ID):
            total += 1

            # Only store valid media types
            if msg.media and msg.media in {
                MessageMediaType.PHOTO,
                MessageMediaType.VIDEO,
                MessageMediaType.ANIMATION,
                MessageMediaType.DOCUMENT
            }:
                is_new = await db.save_media_to_pool(
                    chat_id=MEDIA_CHANNEL_ID,
                    message_id=msg.id,
                    media_type=msg.media.name.lower(),
                    caption=msg.caption or ""
                )
                if is_new:
                    saved += 1
                else:
                    skipped += 1

        await message.reply(
            f"✅ **Indexing Complete!**\n\n"
            f"📦 Total Messages Checked: `{total}`\n"
            f"✅ New Media Saved: `{saved}`\n"
            f"♻️ Skipped (Already in DB): `{skipped}`"
        )

    except Exception as e:
        await message.reply(f"❌ Error during indexing:\n`{e}`")


# 🎲 Pick a random media from the database
async def get_random_media():
    pool = await db.get_all_media()
    if not pool:
        print("[MEDIA] Pool is empty.")
        return None
    return random.choice(pool)
