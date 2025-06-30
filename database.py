from pymongo import MongoClient
from datetime import datetime
import pytz

from config import MONGO_URI
from utils.logger import logger

try:
    client = MongoClient(MONGO_URI)
    db = client["telegram_bot_db"]
    users_collection = db["users"]
    accounts_collection = db["accounts"]
    withdraw_collection = db["withdrawals"]
    logger.info("MongoDB successfully connected.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    exit()


def get_user_data(user_id: int):
    """Fetches user data from the database."""
    return users_collection.find_one({"user_id": user_id})


def create_user_data(user_id: int):
    """Creates a new user entry in the database."""
    user_data = {
        "user_id": user_id,
        "total_balance": 0.0,
        "verified_accounts_count": 0,
        "unverified_accounts_count": 0,
        "join_date": datetime.now(pytz.utc)  # Corrected from join_data
    }
    users_collection.insert_one(user_data)
    return user_data
