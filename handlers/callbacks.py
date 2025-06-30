from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from database import accounts_collection


async def update_timer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'check_remaining' callback query to show time left for verification."""
    query = update.callback_query
    user_id = query.from_user.id

    # Acknowledge the button press
    await query.answer()

    account = accounts_collection.find_one({
        "owner_id": user_id,
        "status": "pending"
    })

    if not account:
        await query.answer("⚠️ No pending verification found.", show_alert=True)
        return

    unlock_time = account['unlock_time']
    now = datetime.now(pytz.utc)
    remaining = (unlock_time - now).total_seconds()

    if remaining <= 0:
        await query.answer(
            "✅ Verification process is complete. Kindly wait for the confirmation message shortly.",
            show_alert=True
        )

    else:
        mins, secs = divmod(int(remaining), 60)
        await query.answer(
            f"⏳ Time remaining: {mins}m {secs}s",
            show_alert=True
        )
