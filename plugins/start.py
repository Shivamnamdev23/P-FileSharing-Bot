import os
import pymongo
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from pyrogram.errors import UserNotParticipant
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FSUB_CHANNEL, DB_URL, OWNER_ID
from helper_func import *
from database.database import add_user, del_user, full_userbase, present_user, get_fsub_channel_id, set_fsub_channel_id, get_fsub_status, set_fsub_status, add_admin, del_admin, full_adminbase
from datetime import datetime

# 1 minutes = 60, 2 minutes = 60×2=120, 5 minutes = 60×5=300
SECONDS = int(os.getenv("SECONDS", "1800"))


@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        await add_user(user_id)
    
    fsub_status = await get_fsub_status()
    FSUB_CHANNEL = await get_fsub_channel_id()

    if fsub_status and FSUB_CHANNEL:
        try:
            await client.get_chat_member(FSUB_CHANNEL, user_id)
        except UserNotParticipant:
            f_link = await client.export_chat_invite_link(FSUB_CHANNEL)
            buttons = [
                [InlineKeyboardButton("⛔ Join Channel ⛔", url=f_link)]
            ]
            if len(message.command) > 1:
                buttons.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://telegram.me/{client.username}?start={message.command[1]}")])

            await message.reply(
                f"<b> ⚠️ Dear {message.from_user.mention} ❗\n\n🙁 First join our channel then you will get your Video, otherwise you will not get it.\n\nClick join channel button 👇\n\nसबसे पहले हमारे चैनल से जुड़ें फिर आपको आपका वीडियो मिलेगा, चैनल से जुड़ें बटन पर क्लिक करें 👇</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    text = message.text
    
    # Handle start command with arguments
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
            
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = list(range(start, end + 1))
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else:
                return
        except:
            return
        
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        
        await temp_msg.delete()
        copied_messages = []
        for msg in messages:
            if bool(CUSTOM_CAPTION) and (bool(msg.document) or bool(msg.video)):
                caption = CUSTOM_CAPTION.format(previouscaption=msg.caption, filename=msg.document.file_name if msg.document else msg.video.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                f = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                copied_messages.append(f)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                f = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                copied_messages.append(f)
            except:
                pass
            
        k = await client.send_message(chat_id=message.from_user.id, text="<b>This video/file will be deleted in 30 minutes (Due to copyright issues).\n\n📌 Please forward this video/file to somewhere else and start downloading there.</b>")
        await asyncio.sleep(600)
        for f in copied_messages:
            await f.delete()
        buttons = [
            [InlineKeyboardButton("Get File Again", url=f"https://telegram.me/{client.username}?start={message.command[1]}")]
        ]
        await k.edit_text("Your video/file is successfully deleted! Click below button to get your deleted file again. 👇</b>", reply_markup=InlineKeyboardMarkup(buttons))
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Join Backup Channel", url="https://t.me/snfilmy")
                ]
            ]
        )
        
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

    
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(text="Join Channel", url=client.invitelink)
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = 'Try Again',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )



@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.command('set_fsub') & filters.private)
async def set_fsub(client: Bot, message: Message):
    if message.text:
        channel_id = message.text.strip()
        await set_fsub_channel_id(channel_id)
        await message.reply("Channel ID has been added to FSUB.")

@Bot.on_message(filters.command('check_fsub') & filters.private)
async def check_fsub(client: Bot, message: Message):
    channel_id = await get_fsub_channel_id()
    if channel_id:
        await message.reply(f"The current FSUB Channel ID is: {channel_id}")
    else:
        await message.reply("No FSUB Channel ID is set.")

@Bot.on_message(filters.command('on_fsub') & filters.private)
async def on_fsub(client: Bot, message: Message):
    await set_fsub_status(True)
    await message.reply("FSUB has been turned ON.")

@Bot.on_message(filters.command('off_fsub') & filters.private)
async def off_fsub(client: Bot, message: Message):
    await set_fsub_status(False)
    await message.reply("FSUB has been turned OFF.")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
        
@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def command_add_admin(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter admin id 🔢\n /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
        except Exception as e:
            print(e)
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error 😖\n\nThe admin id is incorrect.", quote = True)
            continue
    if not await present_admin(admin_id.text):
        try:
            await add_admin(admin_id.text)
            await message.reply(f"Added admin <code>{admin_id.text}</code> 😼")
            try:
                reply_markup = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Join Channel 👆", url=CHANNEL_LINK)]
                    ]
                )
                await client.send_message(
                    chat_id=admin_id.text,
                    text=f"You are verified, join the channel for forwarding links for batch commands. 😁",
                    reply_markup=reply_markup
                )
            except:
                await message.reply("Failed to send invite. Please ensure that they have started the bot. 🥲")
        except:
            await message.reply("Failed to add admin. 😔\nSome error occurred.")
    else:
        await message.reply("admin already exist. 💀")
    return


@Bot.on_message(filters.command('del_admin') & filters.private  & filters.user(OWNER_ID))
async def delete_admin_command(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter admin id 🔢\n /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
        except:
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error\n\nThe admin id is incorrect.", quote = True)
            continue
    if await present_admin(admin_id.text):
        try:
            await del_admin(admin_id.text)
            await message.reply(f"Admin <code>{admin_id.text}</code> removed successfully 😀")
        except Exception as e:
            print(e)
            await message.reply("Failed to remove admin. 😔\nSome error occurred.")
    else:
        await message.reply("admin doesn't exist. 💀")
    return

@Bot.on_message(filters.command('admins')  & filters.private & filters.private)
async def admin_list_command(client: Bot, message: Message):
    admin_list = await full_adminbase()
    await message.reply(f"Full admin list 📃\n<code>{admin_list}</code>")
    return
