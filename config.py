import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Admin and Security Configuration
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TWO_FA_PASSWORD = os.getenv("TWO_FA_PASSWORD")

# Directories
SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
