from telegram import Update
from telegram.ext import ContextTypes
from database import get_user_data, create_user_data
from handlers.auth_flow import PHONE  # Import conversation state


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, greeting the user and initiating the conversation."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    if not user_data:
        user_data = create_user_data(user.id)

    welcome_message = (
        f"👋 **Welcome, {user.first_name}!**\n\n"
        f"🆔 **User ID**: `{user_data['user_id']}`\n\n"
        f"🤖 *This bot helps you seamlessly manage your Telegram accounts.*\n\n"
        f"📱 To get started, please send your phone number in international format:\n"
        f"_Example: +8801234567890_"
    )

    await update.message.reply_text(welcome_message)
    return PHONE
