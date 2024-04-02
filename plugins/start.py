import os
import pymongo
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from pyrogram.errors import UserNotParticipant
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FSUB_CHANNEL
from helper_func import *
from database.database import add_user, del_user, full_userbase, present_user
from datetime import datetime

client = pymongo.MongoClient("mongodb+srv://FileStoreP:FileStoreP@cluster0.mkmkjl8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
tk = client["terabox"]
collection = tk["user_links"]

# 1 minutes = 60, 2 minutes = 60×2=120, 5 minutes = 60×5=300
SECONDS = int(os.getenv("SECONDS", "600"))

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        
        if len(message.text.split(" ")) > 1:
            ad_msg = message.text.split(" ")[1]  
        else:
            ad_msg = None
            
            if not await present_user(user_id):
                try:
                    await add_user(user_id)
                except Exception as e:
                    print(f"Error adding user: {e}")
                    
            if message.text.startswith("/start token_"):
                try:
                    ad_msg = b64_to_str(message.text.split("/start token_")[1])
                    ad_user_id, ad_time = map(int, ad_msg.split(":"))

                    if user_id != ad_user_id:
                        await message.reply_text(
                            "<b>ᴛʜɪꜱ ᴛᴏᴋᴇɴ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ \nᴏʀ ᴍᴀʏʙᴇ ʏᴏᴜ ᴜꜱɪɴɢ 2 ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘꜱ ɪꜰ ʏᴇꜱ ᴛʜᴇɴ ᴜɴɪɴꜱᴛᴀʟʟ ᴛʜɪꜱ ᴏɴᴇ...</b>"
                        )
                        return

                    if ad_time < datetime.now().timestamp():
                        await message.reply_text("Token Expired Regenerate A New Token")
                        return

                    if ad_time > datetime.now().timestamp() + 43200:
                        await message.reply_text("Don't Try To Be Over Smart")
                        return

                    query = {"user_id": user_id}
                    collection.update_one(
                        query, {"$set": {"time_out": ad_time}}, upsert=True
                    )
                    await message.reply_text(
                        "<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ! ᴀᴅꜱ ᴛᴏᴋᴇɴ ʀᴇꜰʀᴇꜱʜᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ!\n\nɪᴛ ᴡɪʟʟ ᴇxᴘɪʀᴇ ᴀꜰᴛᴇʀ 8 ʜᴏᴜʀ.</b>"
                    )
                    return
                    
                    uid = message.from_user.id
                    if uid not in ADMINS:
                        result = collection.find_one({"user_id": uid})
                        if result is None or int(result.get("time_out", 0)) < datetime.now().timestamp():
                            temp_msg = await message.reply("Please wait...")
                            ad_code = str_to_b64(f"{uid}:{str(datetime.now().timestamp() + 43200)}")
                            ad_url = shorten_url(f"https://telegram.dog/{FileStream.username}?start=token_{ad_code}")

                            await client.send_message(
                                message.chat.id,
                                f"Hey 💕 <b>{message.from_user.mention}</b> \n\nYour Ads token is expired, refresh your token and try again. \n\n<b>Token Timeout:</b> 8 hour \n\n<b>What is token?</b> \nThis is an ads token. If you pass 1 ad, you can use the bot for 8 hour after passing the ad. \n\nwatch video tutorial if you're facing issue <a href='https://t.me/jarrydow/2069'>Click Here</a> \n\n<b>APPLE/IPHONE USERS COPY TOKEN LINK AND OPEN IN CHROME BROWSER</b>",
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [
                                            InlineKeyboardButton("Click Here To Verify", url=ad_url)
                                        ], [
                                            InlineKeyboardButton('How to open link and verify', url='https://youtu.be/clgnNlBjm9c?si=PzhpIYzFr6DgGRTz')
                                        ]
                                    ]
                                )
                            )
                            await temp_msg.delete()
                            return
                except Exception as e:
                    print("Error:", e)

    except Exception as e:
        print("Error:", e)
        
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
            
        k = await client.send_message(chat_id=message.from_user.id, text="<b>This video/file will be deleted in 10 minutes (Due to copyright issues).\n\n📌 Please forward this video/file to somewhere else and start downloading there.</b>")
        await asyncio.sleep(600)
        for f in copied_messages:
            await f.delete()
        await k.edit_text("Your video/file is successfully deleted!")
        return
    
    # Handle start command without arguments
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Source Code", url="https://t.me/")],
            [InlineKeyboardButton("😊 About Me", callback_data="about"),
             InlineKeyboardButton("🔒 Close", callback_data="close")]
        ])
        
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
