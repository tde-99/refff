from main import app
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated
from bot.database import reqChannel_exist, reqSent_user_exist, del_reqSent_user, reqSent_user
from pyrogram import Client

@app.on_chat_member_updated()
async def handle_chat_member_update(client, update: ChatMemberUpdated):
    chat_id = update.chat.id
    old = update.old_chat_member

    if not old or old.status != ChatMemberStatus.MEMBER:
        return

    user_id = old.user.id
    if await reqChannel_exist(chat_id) and await reqSent_user_exist(chat_id, user_id):
        await del_reqSent_user(chat_id, user_id)


@app.on_chat_join_request()
async def handle_join_request(client, join_request):
    chat_id = join_request.chat.id
    user_id = join_request.from_user.id

    if await reqChannel_exist(chat_id) and not await reqSent_user_exist(chat_id, user_id):
        await reqSent_user(chat_id, user_id)
