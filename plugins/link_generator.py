from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (With Quotes)..\n\nOr Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://filescrazy.blogspot.com/2024/07/files.html?link={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📁 Files Link", url=f'{link}'),InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>✅ Your <a href='{link}'>Link</a> has been generated!\n\n👇 You can access the all files using the link below.\n\n<code>{link}</code>\n\n(👆 Tap to copy)</b>", quote=True, reply_markup=reply_markup)
    store_channel_id = -1002233798221
    for msg_id in range(f_msg_id, s_msg_id + 1):
        try:
            message = await client.get_messages(client.db_channel.id, msg_id)
            if message.document:
                await client.send_document(
                    chat_id=store_channel_id,
                    document=message.document.file_id,
                    caption=message.caption
                )
            elif message.photo:
                await client.send_photo(
                    chat_id=store_channel_id,
                    photo=message.photo.file_id,
                    caption=message.caption
                )
            elif message.video:
                await client.send_video(
                    chat_id=store_channel_id,
                    video=message.video.file_id,
                    caption=message.caption
                )
            # Add more conditions if there are other types of media you want to handle
        except Exception as e:
            print(f"Failed to send message {msg_id}: {e}")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://filescrazy.blogspot.com/2024/07/files.html?link={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
