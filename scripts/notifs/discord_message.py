import requests
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


def send_discord_message(message, username = "Bird Scraper"):
    webhook = os.getenv("DISCORD_WEBHOOK")

    if not webhook:
        raise ValueError(
            "DISCORD_WEBHOOK_URL is missing from the .env file"
        )

    # Discord messages have a 2000 character content limit
    message = message[:2000]

    response = requests.post(
        webhook,
        json = {
            "username": username,
            "content": message,
        },
        timeout = 10,
    )

    response.raise_for_status()