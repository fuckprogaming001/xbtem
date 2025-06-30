from datetime import datetime
import pytz
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database import get_user_data, withdraw_collection, users_collection

# Conversation state
CARD_NAME = range(1)


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the withdrawal process."""
    # context.user_data.clear()
    print(context)
    await update.message.reply_text(
        "💳 *Please enter your card name* to proceed with the withdrawal request.\n\n"
        "📌 _Example: BEP 20, TRC 20_\n"
        "⚠️ *Note:* Withdrawals are only supported for **Leader** cards at this time.",
    )
    return CARD_NAME


async def handle_card_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles receiving the card name and processes the withdrawal request."""
    card_name = update.message.text.strip()
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)

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

    await update.message.reply_text(
        f"✅ *Withdrawal Request Received!*\n\n"
        f"💳 You've requested a withdrawal for the *'{card_name}'* card.\n"
        f"🕵️‍♂️ Our admin team is reviewing your request and will get back to you shortly.\n\n"
        f"📌 _Please wait while we process it. Thank you for your patience!_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    # return ConversationHandler.END
