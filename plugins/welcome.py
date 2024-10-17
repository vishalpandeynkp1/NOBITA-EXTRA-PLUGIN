from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops

def create_gradient_background(size):
    """Create a gradient background."""
    gradient = Image.new("RGBA", size)
    for y in range(size[1]):
        r = int(0 + (255 - 0) * (y / size[1]))
        g = int(0 + (191 - 0) * (y / size[1]))
        b = int(255 * (y / size[1]))
        for x in range(size[0]):
            gradient.putpixel((x, y), (r, g, b, 255))
    return gradient

def circle(pfp, size=(100, 100), brightness_factor=1.2):
    """Create a circular profile picture with a colored border."""
    pfp = pfp.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    # Create circular mask
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.Resampling.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)

    # Create border outlines
    border_sizes = [5, 3, 3]  # Violet, Blue, Green
    colors = [(148, 0, 211), (0, 0, 255), (19, 136, 8)]  # Violet, Blue, Green

    outline = Image.new("RGBA", (pfp.size[0] + 2 * border_sizes[0], pfp.size[1] + 2 * border_sizes[0]), (0, 0, 0, 0))
    outline_draw = ImageDraw.Draw(outline)

    for i, (border_size, color) in enumerate(zip(border_sizes, colors)):
        outline_draw.ellipse((border_size * i, border_size * i, outline.size[0] - border_size * i, outline.size[1] - border_size * i), outline=color, width=border_size)

    outline.paste(pfp, (border_sizes[0], border_sizes[0]), pfp)

    return outline

def draw_shadowed_text(draw, position, text, font, text_color, shadow_color=(0, 0, 0), shadow_offset=(2, 2)):
    """Draw text with shadow effect."""
    # Draw shadow
    draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), text, fill=shadow_color, font=font)
    # Draw text
    draw.text(position, text, fill=text_color, font=font)

def welcomepic(user_id, user_username, user_names, chat_name, user_photo, chat_photo):
    """Generate a welcome image for a new member."""
    try:
        # Create a gradient background
        background_size = (1080, 720)
        background = create_gradient_background(background_size)

        user_img = Image.open(user_photo).convert("RGBA")
        chat_img = Image.open(chat_photo).convert("RGBA")

        chat_img_circle = circle(chat_img, size=(240, 240), brightness_factor=1.2)
        user_img_circle = circle(user_img, size=(232, 232), brightness_factor=1.2)

        # Define positions for images
        background.paste(chat_img_circle, (270, 100), chat_img_circle)
        background.paste(user_img_circle, (820, 100), user_img_circle)

        draw = ImageDraw.Draw(background)
        # Load font with different styles
        font_large = ImageFont.truetype("assets/font.ttf", size=56)  # Increased size for emphasis
        font_medium = ImageFont.truetype("assets/font.ttf", size=40)
        font_small = ImageFont.truetype("assets/font.ttf", size=32)

        # Define colors for text
        text_colors = {
            "name": (255, 153, 51),  # Saffron
            "id": (255, 255, 255),    # White
            "username": (19, 136, 8)   # Green
        }

        # Define text positions
        text_positions = {
            "name": (500, 380),  # Centered below the profile picture
            "id": (500, 440),    # Centered below name
            "username": (500, 500)  # Centered below ID
        }

        # Draw shadowed text on image
        draw_shadowed_text(draw, text_positions["name"], f"Welcome, {user_names}!", font_large, text_colors["name"])
        draw_shadowed_text(draw, text_positions["id"], f"User Id: {user_id}", font_medium, text_colors["id"])
        draw_shadowed_text(draw, text_positions["username"], f"Username: {user_username}", font_small, text_colors["username"])

        # Add a welcoming message
        welcome_message = "We're glad to have you here!"
        draw_shadowed_text(draw, (500, 570), welcome_message, font_small, (255, 255, 255))

        # Save the welcome image
        welcome_image_path = f"downloads/welcome#{user_id}.png"
        background.save(welcome_image_path)
        return welcome_image_path

    except Exception as e:
        LOGGER.error(f"Error generating welcome image: {e}")
        return "assets/nodp.png"  # Return a default image on error
