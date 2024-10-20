import asyncio
import re
import time
from logging import getLogger
from time import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated
import config
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant
from pytz import timezone
from datetime import datetime

user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

LOGGER = getLogger(__name__)

def convert_to_small_caps(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢ",
    )
    return text.translate(mapping)

class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "on"}

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]

wlcm = WelDatabase()

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None

@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        A = await wlcm.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        if state == "off":
            if A:
                await message.reply_text("**ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !**")
            else:
                await wlcm.add_wlcm(chat_id)
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title} ʙʏ ʙᴏᴛ**")
        elif state == "on":
            if not A:
                await message.reply_text("**ᴇɴᴀʙʟᴇᴅ ʙᴏᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.**")
            else:
                await wlcm.rm_wlcm(chat_id)
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ʙᴏᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ʙᴏᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**")

def circle(pfp, size=(400, 400), brightness_factor=1.2):
    try:
        pfp = pfp.resize(size, Image.LANCZOS).convert("RGBA")
        pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

        mask = Image.new("L", (size[0], size[1]), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        pfp.putalpha(mask)

        outline_size = 10
        outline = Image.new("RGBA", (size[0] + outline_size * 2, size[1] + outline_size * 2), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline)

        outline_draw.ellipse((0, 0, outline.size[0], outline.size[1]), fill=(148, 0, 211, 255))
        outline_draw.ellipse((outline_size, outline_size, outline.size[0] - outline_size, outline.size[1] - outline_size), fill=(0, 0, 255, 255))

        outline.paste(pfp, (outline_size, outline_size), pfp)

        return outline
    except Exception as e:
        LOGGER.error(f"Error creating circular image: {e}")
        return None

def welcomepic(user_id, user_username, user_names, chat_name, user_photo, chat_photo):
    try:
        background = Image.open("assets/wel2.png").convert("RGBA")
        user_img = Image.open(user_photo).convert("RGBA")

        user_img_circle = circle(user_img, size=(400, 400))

        if user_img_circle:
            background.paste(user_img_circle, (210, 220), user_img_circle)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("assets/font.ttf", size=32)
        
        text_color = (255, 255, 255)
        shadow_color = (0, 0, 0)

        draw.text((50 + 2, 100 + 2), f"Welcome to {chat_name}", font=font, fill=shadow_color)
        draw.text((50, 100), f"Welcome to {chat_name}", font=font, fill=text_color)

        output_path = f"downloads/welcome#{user_id}.png"
        background.save(output_path)
        return output_path
    except Exception as e:
        LOGGER.error(f"Error creating welcome image: {e}")
        return None

@app.on_chat_member_updated(filters.group, group=-4)
async def greet_new_members(_, member: ChatMemberUpdated):
    try:
        chat_id = member.chat.id
        chat = await app.get_chat(chat_id)
        user = member.new_chat_member.user
        user_id = user.id

        chat_name = chat.title if chat.title else "Anjan Group"
        user_username = f"@{user.username}" if user.username else "No Username"
        user_name = user.first_name if user.first_name else "No Name"

        ist = timezone('Asia/Kolkata')
        joined_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

        if member.new_chat_member and not member.old_chat_member:
            user_photo = "assets/nodp.png"
            chat_photo = "assets/nodp.png


__MODULE__ = "Wᴇᴄᴏᴍᴇ"
__HELP__ = """
## Aᴜᴛᴏ-Wᴇᴄᴏᴍᴇ Mᴏᴅᴜᴇ Cᴏᴍᴍᴀɴᴅs

### Cᴏᴍᴍᴀɴᴅ: /ᴀᴡᴇᴄᴏᴍᴇ
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Eɴᴀʙᴇs ᴏʀ ᴅɪsᴀʙᴇs ᴛʜᴇ ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ғᴇᴀᴛᴜʀᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ.

**Usᴀɢᴇ:**
/welcome [ᴏɴ|ᴏғғ] (ғᴏʀ ʙᴏᴛ)

/awelcome [ᴏɴ|ᴏғғ] (ғᴏʀ ᴀssɪsᴛᴀɴᴄᴇ)

**Dᴇᴛᴀɪs:**
- ᴏɴ: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.
- ᴏғғ: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.

**Nᴏᴛᴇs:**
- Oɴʏ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs ᴀɴᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.

### Sᴘᴀᴍ Pʀᴏᴛᴇᴄᴛɪᴏɴ
Pʀᴇᴠᴇɴᴛs ᴄᴏᴍᴍᴀɴᴅ sᴘᴀᴍᴍɪɴɢ. Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴏʀᴇ ᴛʜᴀɴ 2 ᴄᴏᴍᴍᴀɴᴅs ᴡɪᴛʜɪɴ 5 sᴇᴄᴏɴᴅs, ᴛʜᴇʏ ᴡɪ ʙᴇ ᴡᴀʀɴᴇᴅ ᴀɴᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʏ ʙᴏᴄᴋᴇᴅ.

### Wᴇᴄᴏᴍᴇ Nᴇᴡ Mᴇᴍʙᴇʀs
Aᴜᴛᴏᴍᴀᴛɪᴄᴀʏ sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡʜᴏ ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

**Bᴇʜᴀᴠɪᴏʀ:**
- Sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴍᴇɴᴛɪᴏɴɪɴɢ ᴛʜᴇ ɴᴇᴡ ᴜsᴇʀ.
- Tʜᴇ ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴀғᴛᴇʀ ᴀ 3-sᴇᴄᴏɴᴅ ᴅᴇᴀʏ.

### Exᴀᴍᴘᴇs
- /awelcome on: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.
- /awelcome off: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.

Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴜᴛɪᴘᴇ ᴄᴏᴍᴍᴀɴᴅs ǫᴜɪᴄᴋʏ:
Tʜᴇʏ ᴡɪ ʀᴇᴄᴇɪᴠᴇ ᴀ sᴘᴀᴍ ᴡᴀʀɴɪɴɢ.
"""
