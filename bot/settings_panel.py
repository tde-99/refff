from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS, MEDIA_CHANNEL_ID
from bot import database as db
from bot.media import get_random_media


# ✅ Admin Panel Entry Point
async def open_settings_panel(client: Client, message: Message):
    if message.from_user.id not in ADMINS:
        print(f"[DENIED] User {message.from_user.id} is not in ADMINS")
        return await message.reply("🚫 You are not authorized to use this command.")
    
    print(f"[SETTINGS] Access granted to {message.from_user.id}")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 Set Force-Sub Channel", callback_data="add_fsub")],
        [
            InlineKeyboardButton("🎞️ Index Media", callback_data="set_media"),
            InlineKeyboardButton("👁 Preview Media", callback_data="preview_media")
        ],
        [InlineKeyboardButton("📊 View Stats", callback_data="view_stats")]
    ])
    await message.reply(
        "🛠 **Welcome to the Admin Panel**\nUse the buttons below to configure your bot 👇",
        reply_markup=buttons
    )


# ✅ Set Force-Sub Channel
async def add_fsub_handler(client: Client, callback_query: CallbackQuery):
    await db.set_setting("awaiting_fsub", callback_query.from_user.id)
    await callback_query.message.edit(
        "📨 Please *forward* any post from your **Force-Sub Channel** to me now.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]])
    )
    await callback_query.answer("Waiting for forwarded message...")


# ✅ Handle Forwarded Message
async def handle_forwarded_channel(client: Client, message: Message):
    awaiting = await db.get_setting("awaiting_fsub")
    if not awaiting or int(awaiting) != message.from_user.id:
        print(f"[FORWARD IGNORED] No awaiting_fsub for {message.from_user.id}")
        return

    try:
        channel_id = message.forward_from_chat.id
        print(f"[FORWARD] Received channel ID: {channel_id}")
        member = await client.get_chat_member(channel_id, "me")
        if member.status not in ["administrator", "creator"]:
            return await message.reply("❌ I am not an admin in that channel. Please add me first.")

        await db.set_setting("force_sub_channel", channel_id)
        await db.add_req_channel(channel_id)
        await db.set_setting("awaiting_fsub", None)
        await message.reply(f"✅ Force-sub channel has been saved: `{channel_id}`")
    except Exception as e:
        await message.reply(f"❌ Error saving channel: `{e}`")


# ✅ Index Media
async def set_media_handler(client: Client, callback_query: CallbackQuery):
    from bot.media import set_media_pool
    await set_media_pool(client, callback_query.message)
    await callback_query.answer("✅ Media indexed successfully.")


# ✅ Preview Random Media
async def preview_handler(client: Client, callback_query: CallbackQuery):
    media = await get_random_media()
    if not media:
        return await callback_query.message.edit("⚠️ Media pool is empty. Please index some content first.")

    try:
        await client.copy_message(
            chat_id=callback_query.message.chat.id,
            from_chat_id=media["chat_id"],
            message_id=media["message_id"]
        )
        await callback_query.answer("✅ Media previewed.")
    except Exception as e:
        await callback_query.message.reply(f"❌ Failed to preview media:\n`{e}`")


# ✅ View Stats
async def stats_handler(client: Client, callback_query: CallbackQuery):
    users = await db.get_all_users()
    total_users = len(list(users))
    total_refs = await db.count_total_referrals()

    await callback_query.message.edit(
        f"📊 **Bot Statistics:**\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"🔗 Total Referrals: `{total_refs}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]])
    )
    await callback_query.answer()


# 🔙 Back to Main Panel
async def back_to_settings(client: Client, callback_query: CallbackQuery):
    await open_settings_panel(client, callback_query.message)
    await callback_query.answer("Returned to settings.")
