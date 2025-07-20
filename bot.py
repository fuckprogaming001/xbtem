import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
    ConversationHandler
)
import logging
from handlers.account import download_sessions


# Local imports
from config import BOT_TOKEN
from utils.logger import logger
from services.monitor import monitor_pending_verifications

# Import handlers
from handlers.start import start
from handlers.auth_flow import (
    get_phone,
    get_code,
    cancel,
    PHONE,
    CODE,
)
from handlers.withdraw import (
    withdraw,
    handle_card_name,
    CARD_NAME,
)
from handlers.account import account
from handlers.callbacks import update_timer_callback


def main():
    """Main function to set up and run the bot."""

    async def post_init(app: Application):
        """Create a background task for monitoring after the application starts."""
        asyncio.create_task(monitor_pending_verifications(app.bot))
        logger.info("Background monitoring task started.")
    
    # Build the application
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # --- Conversation Handlers ---

    # Authentication Flow (start -> phone -> code)
    auth_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r"^\+\d{11,15}$"), get_phone)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
        conversation_timeout=300,
    )

    # Withdrawal Flow (withdraw -> card_name)
    withdraw_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("withdraw", withdraw)],
        states={
            CARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^\+\d{11,15}$"), handle_card_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
        conversation_timeout=300,

    )

    # --- Register Handlers ---
    app.add_handler(auth_conv_handler)
    app.add_handler(withdraw_conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("account", account))
    app.add_handler(CommandHandler("cancel", cancel))  # General cancel command
    app.add_handler(CommandHandler("download_sessions", download_sessions))

    # Callback handler for inline buttons
    app.add_handler(CallbackQueryHandler(
        # pattern="^check_remaining$"
        update_timer_callback))

    # --- Start the Bot ---
    logger.info("🤖 Bot is starting...")
    app.run_polling(poll_interval=5, timeout=30)
    logger.info("Bot has stopped.")


if __name__ == "__main__":
    main()


# demo


# import asyncio
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ConversationHandler,
#     CallbackQueryHandler,
#     ConversationHandler
# )
# from handlers.account import download_sessions


# # Local imports
# from config import BOT_TOKEN
# from utils.logger import logger
# from services.monitor import monitor_pending_verifications

# # Import handlers
# from handlers.start import start
# from handlers.auth_flow import (
#     get_phone,
#     get_code,
#     cancel,
#     PHONE,
#     CODE,
# )
# from handlers.withdraw import (
#     withdraw,
#     handle_card_name,
#     CARD_NAME,
# )
# from handlers.account import account
# from handlers.callbacks import update_timer_callback


# def main():
#     """Main function to set up and run the bot."""

#     async def post_init(app: Application):
#         """Create a background task for monitoring after the application starts."""
#         asyncio.create_task(monitor_pending_verifications(app.bot))
#         logger.info("Background monitoring task started.")

#     # Build the application
#     app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

#     # --- Conversation Handlers ---

#     # Authentication Flow (start -> phone -> code)
#     auth_conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", start)],
#         states={
#             PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r"^\+\d{11,15}$"), get_phone)],
#             CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#         per_chat=True,
#         conversation_timeout=300,
#     )

#     # Withdrawal Flow (withdraw -> card_name)
#     withdraw_conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("withdraw", withdraw)],
#         states={
#             CARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^\+\d{11,15}$"), handle_card_name)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#         per_chat=True,
#         conversation_timeout=300,

#     )

#     # --- Register Handlers ---
#     app.add_handler(auth_conv_handler)
#     app.add_handler(withdraw_conv_handler)
#     app.add_handler(CommandHandler("account", account))
#     app.add_handler(CommandHandler("cancel", cancel))  # General cancel command
#     app.add_handler(CommandHandler("download_sessions", download_sessions))

#     # Callback handler for inline buttons
#     app.add_handler(CallbackQueryHandler(
#         update_timer_callback, pattern="^check_remaining$"))

#     # --- Start the Bot ---
#     logger.info("🤖 Bot is starting...")
#     app.run_polling()
#     logger.info("Bot has stopped.")


# if __name__ == "__main__":
#     main()
