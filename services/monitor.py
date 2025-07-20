import asyncio
from datetime import datetime
import pytz
from database import accounts_collection, users_collection, get_user_data
from utils.logger import logger
from telethon.sync import TelegramClient
from config import API_ID, API_HASH


from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    SessionPasswordNeededError,
    PhoneNumberBannedError,
    AuthKeyUnregisteredError
)


async def is_account_valid(session_string, api_id, api_hash):
    try:
        async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
            me = await client.get_me()
            return True, me.phone  # Valid account
    except (UserDeactivatedBanError, PhoneNumberBannedError, AuthKeyUnregisteredError) as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


async def monitor_pending_verifications(bot):
    """Periodically checks for accounts ready for verification and notifies users."""
    while True:
        now = datetime.now(pytz.utc)
        pending_accounts = accounts_collection.find({
            "status": "pending",
            "unlock_time": {"$lte": now}
        })

        for account in pending_accounts:
            chat_id = account["chat_id"]
            owner_id = account["owner_id"]
            price = account["price"]
            phone_number = account["phone_number"]
            session_string = account.get("session_string")
            try:

                is_valid, msg = await is_account_valid(session_string, API_ID, API_HASH)
                if not is_valid:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            "🎉 <b>We have processed your account</b>\n\n"
                            f"<b>Number:</b> <code>{phone_number}</code>\n"
                            f"<b>Price:</b> $0\n"
                            f"<b>Status:</b> ❄️ <u>Frozen</u>\n\n"
                            "⚠️ Unfortunately, this account is not usable and has not been added to your balance."
                        ),
                        parse_mode="HTML"
                    )

                    accounts_collection.update_one(
                        {"_id": account["_id"]},
                        {"$set": {"status": "failed", "error_message": msg}}
                    )

                    users_collection.update_one(
                        {"user_id": owner_id},
                        {
                            "$inc": {"unverified_accounts_count": -1}
                        }
                    )

                    logger.warning(
                        f"Invalid account detected: {phone_number} | Reason: {msg}")
                    continue  # Skip to next account
                    # Notify the user
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"✅ Verification complete for account: {phone_number}!\n\n"
                        f"A balance of ${price:.2f} has been added to your account."
                    )
                )

                # Update user data
                users_collection.update_one(
                    {"user_id": owner_id},
                    {
                        "$inc": {
                            "verified_accounts_count": 1,
                            "unverified_accounts_count": -1,
                            "total_balance": price
                        }
                    }
                )

                # Update account status
                accounts_collection.update_one(
                    {"_id": account["_id"]},
                    {"$set": {"status": "verified"}}
                )
                logger.info(
                    f"Verified account {phone_number} for user {owner_id}")

            except Exception as e:
                logger.error(
                    f"Error processing verification for {phone_number}: {e}")

        # Wait for 60 seconds before the next check
        await asyncio.sleep(60)
