import requests
import random
import re
import asyncio
from MukeshAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction, ParseMode
from VIPMUSIC import app

# List of supported emojis for reactions
EMOJI_LIST = [
    "👍", "👎", "❤️", "🔥", "🥳", "👏", "😁", "😂", "😲", "😱", 
    "😢", "😭", "🎉", "😇", "😍", "😅", "💩", "🙏", "🤝", "🍓", 
    "🎃", "👀", "💯", "😎", "🤖", "🐵", "👻", "🎄", "🥂", "🎅", 
    "❄️", "✍️", "🎁", "🤔", "💔", "🥰", "😢", "🥺", "🙈", "🤡", 
    "😋", "🎊", "🍾", "🌟", "👶", "🦄", "💤", "😷", "👨‍💻", "🍌", 
    "🍓", "💀", "👨‍🏫", "🤝", "☠️", "🎯", "🍕", "🦾", "🔥", "💃"
]

# Function to send a random emoji reaction
async def react_with_random_emoji(client, message):
    try:
        emoji = random.choice(EMOJI_LIST)
        await app.send_reaction(message.chat.id, message.id, emoji)
    except Exception as e:
        print(f"Failed to send reaction: {str(e)}")

# Function to convert text to small caps
def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }

    words = text.split()
    transformed_words = []
    
    for word in words:
        if word.startswith('@'):
            transformed_words.append(word)
        else:
            transformed_words.append(''.join(small_caps.get(char, char) for char in word.lower()))

    return ' '.join(transformed_words)

# Function to determine if the response contains a link
def contains_link(text):
    return bool(re.search(r'http[s]?://', text))

# Function to format the response based on content
def format_response(text):
    if contains_link(text):
        return text
    else:
        return to_small_caps(text)

# Function to truncate text to a maximum of 50 words
def truncate_text(text, max_words=50):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + "..."
    return text

# Function to gradually reveal the message in 4 steps
async def gradual_message_edit(message, text, delay=0.1):
    words = text.split()
    chunk_size = max(1, len(words) // 4)  # Divide the total number of words by 4
    
    for i in range(1, 5):
        chunk = ' '.join(words[:i * chunk_size])
        await message.edit(chunk)
        await asyncio.sleep(delay)

# Handler for direct messages (DMs)
@app.on_message(filters.private & ~filters.service)
async def gemini_dm_handler(client, message):
    await react_with_random_emoji(client, message)
    sent_message = await message.reply_text("...")
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    user_input = message.text

    try:
        response = api.gemini(user_input)
        x = response.get("results")
        image_url = response.get("image_url")

        if x:
            formatted_response = format_response(truncate_text(x))
            if image_url:
                await message.reply_photo(image_url, caption=formatted_response, quote=True)
            else:
                await gradual_message_edit(sent_message, formatted_response)
        else:
            await gradual_message_edit(sent_message, to_small_caps("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ"))
    except requests.exceptions.RequestException as e:
        pass

# Handler for group chats when replying to the bot's message or mentioning the bot
@app.on_message(filters.group)
async def gemini_group_handler(client, message):
    bot_username = (await app.get_me()).username

    if message.text:
        if message.reply_to_message and message.reply_to_message.from_user.username == bot_username:
            await react_with_random_emoji(client, message)
            sent_message = await message.reply_text("...")
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)

            user_input = message.text.strip()
            try:
                response = api.gemini(user_input)
                x = response.get("results")
                image_url = response.get("image_url")

                if x:
                    formatted_response = format_response(truncate_text(x))
                    if image_url:
                        await message.reply_photo(image_url, caption=formatted_response, quote=True)
                    else:
                        await gradual_message_edit(sent_message, formatted_response)
                else:
                    await gradual_message_edit(sent_message, to_small_caps("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ"))
            except requests.exceptions.RequestException as e:
                pass
        
        elif f"@{bot_username}" in message.text:
            await react_with_random_emoji(client, message)
            sent_message = await message.reply_text("...")
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)

            user_input = message.text.replace(f"@{bot_username}", "").strip()

            try:
                response = api.gemini(user_input)
                x = response.get("results")
                image_url = response.get("image_url")

                if x:
                    formatted_response = format_response(truncate_text(x))
                    if image_url:
                        await message.reply_photo(image_url, caption=formatted_response, quote=True)
                    else:
                        await gradual_message_edit(sent_message, formatted_response)
                else:
                    await gradual_message_edit(sent_message, to_small_caps("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ"))
            except requests.exceptions.RequestException as e:
                pass