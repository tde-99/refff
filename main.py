from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, ChatMemberUpdatedHandler, ChatJoinRequestHandler
from config import API_ID, API_HASH, BOT_TOKEN
from bot.start import start_command
from bot.settings_panel import (
    open_settings_panel,
    add_fsub_handler,
    handle_forwarded_channel,
    set_media_handler,
    preview_handler,
    stats_handler,
    back_to_settings,
)
from bot.media import set_media_pool
from bot.req_fsub import handle_chat_member_update, handle_join_request

app = Client(
    "referral_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# start
app.add_handler(MessageHandler(start_command, filters.command("start")))

# settings
app.add_handler(MessageHandler(open_settings_panel, filters.command("settings")))
app.add_handler(CallbackQueryHandler(add_fsub_handler, filters.regex("add_fsub")))
app.add_handler(MessageHandler(handle_forwarded_channel, filters.forwarded))
app.add_handler(CallbackQueryHandler(set_media_handler, filters.regex("set_media")))
app.add_handler(CallbackQueryHandler(preview_handler, filters.regex("preview_media")))
app.add_handler(CallbackQueryHandler(stats_handler, filters.regex("view_stats")))
app.add_handler(CallbackQueryHandler(back_to_settings, filters.regex("back_to_settings")))

# media
app.add_handler(MessageHandler(set_media_pool, filters.command("setmedia")))

# fsub
app.add_handler(ChatMemberUpdatedHandler(handle_chat_member_update))
app.add_handler(ChatJoinRequestHandler(handle_join_request))


if __name__ == "__main__":
    print("🤖 Bot is starting...")
    app.run()
