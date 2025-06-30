import asyncio
from datetime import datetime
import pytz
from database import accounts_collection, users_collection, get_user_data
from utils.logger import logger


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

            try:
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
