import requests
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats','set_fsub','check_fsub','on_fsub','off_fsub']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://filescrazy.blogspot.com/2024/06/mode.html?link={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📁 File Link", url=f'{link}'),InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>✅ Your <a href='{link}'>Link</a> has been generated!\n\n👇 You can access the file using the link below.\n\n<code>{link}</code>\n\n(👆 Tap to copy)</b>", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)
        
@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://filescrazy.blogspot.com/2024/06/mode.html?link={base64_string}"
    caption = f"{message.caption}\n\n✅ Link Here <a href='{link}'>Link</a>" if message.caption else link
    try:
        await message.edit_caption(caption=caption, reply_markup=None)
    except Exception as e:
        print(e)
        pass
