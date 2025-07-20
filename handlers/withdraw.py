from datetime import datetime
import pytz
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database import get_user_data, withdraw_collection, users_collection
from config import TELEGRAM_ADMIN_CHANNEL_ID, ADMIN_ID
# Conversation state
CARD_NAME = range(1)


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(context)
    await update.message.reply_text(
        "💳 *Please enter your card name* to proceed with the withdrawal request.\n\n"
        "📌 _Example: BEP 20, TRC 20_\n"
        "⚠️ *Note:* Withdrawals are only supported for **Leader** cards at this time.",
        parse_mode="Markdown"  # Added parse_mode for proper formatting in this initial message
    )
    return CARD_NAME


async def handle_card_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles receiving the card name and processes the withdrawal request."""
    card_name = update.message.text.strip()
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    username = update.effective_user.username if update.effective_user.username else f"user_{user_id}"

    if not user_data or user_data["total_balance"] <= 0:
        await update.message.reply_text("You have no balance to withdraw.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    withdraw_collection.insert_one({
        "user_id": user_id,
        "card_name": card_name,
        "withdrawal_balance": user_data["total_balance"],
        "request_time": datetime.now(pytz.utc),
        "status": "pending"
    })

    # Reset user's balance and verified accounts count
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"total_balance": 0, "verified_accounts_count": 0}}
    )

    message_to_channel = (
        f"💰 *New Withdrawal Request!* 💰\n\n"
        f"👤 User: @`{username}`\n"
        f"💳 Card Name: `{card_name}`\n"
        f"💵 *Amount:* `{user_data["total_balance"]}`\n"
        f"⏰ Request Time (UTC): `{datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"📝 *Status:* `Pending`"
    )

    try:
        await context.bot.send_message(
            chat_id=TELEGRAM_ADMIN_CHANNEL_ID,
            text=message_to_channel,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending message to admin channel: {e}")

    try:
        await update.message.reply_text(
            f"✅ *Withdrawal Request Received!*\n\n"
            f"💳 You've requested a withdrawal for the *'{card_name}'* card.\n"
            f"🕵️‍♂️ Our admin team is reviewing your request and will get back to you shortly.\n\n"
            f"📌 _Please wait while we process it. Thank you for your patience!_",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        print("Message sent to user.")  # Debugging
    except Exception as e:
        print(f"Error sending message to user: {e}")

    return ConversationHandler.END
