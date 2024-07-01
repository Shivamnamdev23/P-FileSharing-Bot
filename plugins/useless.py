from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time



@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))

@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💢 ᴊᴏɪɴ ɴᴏᴡ 💢", url="https://t.me/+v6h3boTBQXZlYWU1")]
        ]
    )
    await message.reply(
        "ꜰᴏʀ ɴᴇᴡ ᴍᴏᴠɪᴇꜱ ᴏʀ ᴡᴇʙ ꜱᴇʀɪᴇꜱ, ᴄʟɪᴄᴋ ᴛʜᴇ ᴊᴏɪɴ ɴᴏᴡ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.\n\nनई फिल्में या वेब सीरीज के लिए नीचे दिए गए 'Join Now' बटन पर क्लिक करें।",
        reply_markup=reply_markup
    )
