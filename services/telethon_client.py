# services/telethon_client.py

from telethon import TelegramClient
from config import API_ID, API_HASH
import asyncio

SESSIONS_DIR = "sessions"


async def is_session_active(session_name: str) -> bool:
    session_path = f"{SESSIONS_DIR}/{session_name}"
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        await client.connect()
        is_authorized = await client.is_user_authorized()
        await client.disconnect()
        return is_authorized
    except Exception as e:
        print(f"Error checking session {session_name}: {e}")
        if client.is_connected():
            await client.disconnect()
        return False
