from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the new member
    user = update.effective_user
    chat = update.effective_chat

    user_id = user.id
    user_username = user.username if user.username else "No Username"
    user_names = user.full_name
    user_photo = await user.get_profile_photo().get_url() if user.get_profile_photo() else "default_profile_pic.png"
    chat_photo = await chat.get_profile_photo().get_url() if chat.get_profile_photo() else "default_chat_pic.png"
    member_count = chat.get_members_count()

    # Customize the welcome message
    greeting = f"🎉 Welcome to our group, {user_names}! 🎉"
    group_info = f"👥 Group: {chat.title}\n📈 Members: {member_count}"

    # Generate the welcome image
    welcome_image_path = welcomepic(user_id, user_username, user_names, chat.title, user_photo, chat_photo)

    # Send the welcome image
    with open(welcome_image_path, 'rb') as photo:
        await context.bot.send_photo(chat.id, photo=photo, caption=f"{greeting}\n{group_info}")

    # Optional: Add inline buttons
    keyboard = [
        [
            InlineKeyboardButton("Rules", callback_data='rules'),
            InlineKeyboardButton("Get Help", callback_data='get_help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat.id, "Click below for more options:", reply_markup=reply_markup)

# Function to create a welcome image (modify this function as per your design requirements)
def welcomepic(user_id, user_username, user_names, group_title, user_photo, chat_photo):
    # Example function to create a welcome image
    # Use PIL or any other image processing library to create the welcome image
    # Add user_photo and chat_photo to the image, overlay text, etc.
    # Return the path to the created image
    return "path_to_welcome_image.png"
