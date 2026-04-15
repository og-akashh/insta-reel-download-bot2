import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")

    PORT = int(os.getenv("PORT", 8000))

    # Download settings
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "downloads")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", 300))
    DELETE_AFTER_MINUTES = int(os.getenv("DELETE_AFTER_MINUTES", 20))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Channels to verify join
    # Format: list of (channel_id, invite_link) or (channel_username, invite_link)
    # We'll parse from environment variables
    REQUIRED_CHANNELS = []
    
    @classmethod
    def load_channels(cls):
        """Load required channels from env variables."""
        channels_str = os.getenv("REQUIRED_CHANNELS", "")
        if channels_str:
            for item in channels_str.split(';'):
                parts = item.strip().split(',')
                if len(parts) == 2:
                    cls.REQUIRED_CHANNELS.append({
                        "identifier": parts[0].strip(),
                        "invite_link": parts[1].strip()
                    })
        else:
            # Fallback: look for CHANNEL_1_LINK, CHANNEL_1_ID etc.
            i = 1
            while True:
                link = os.getenv(f"CHANNEL_{i}_LINK")
                cid = os.getenv(f"CHANNEL_{i}_ID")
                if not link:
                    break
                cls.REQUIRED_CHANNELS.append({
                    "identifier": cid or link,
                    "invite_link": link
                })
                i += 1

    OWNER_LINK = os.getenv("OWNER_LINK", "https://t.me/")
    SUPPORT_CHANNEL_LINK = os.getenv("SUPPORT_CHANNEL_LINK", "https://t.me/")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        cls.ensure_download_dir()
        cls.load_channels()

    @classmethod
    def ensure_download_dir(cls):
        os.makedirs(cls.DOWNLOAD_PATH, exist_ok=True)
