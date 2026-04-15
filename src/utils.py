import logging
import re
import os
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def setup_logging(level):
    logger.setLevel(level)
    return logger

def is_instagram_url(url: str) -> bool:
    patterns = [
        r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/(p|reel|tv|stories)/[a-zA-Z0-9_-]+",
        r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/[a-zA-Z0-9_.]+/?(p|reel|tv|stories)/?",
    ]
    return any(re.match(p, url) for p in patterns)

def is_youtube_url(url: str) -> bool:
    patterns = [
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/(shorts|watch|playlist|embed|v)/[a-zA-Z0-9_-]+",
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.*v=[a-zA-Z0-9_-]+",
    ]
    return any(re.match(p, url) for p in patterns)

def is_supported_url(url: str) -> bool:
    return is_instagram_url(url) or is_youtube_url(url)

async def delete_file_async(file_path: str, delay_seconds: int = 0):
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")

def safe_filename(title: str, ext: str = "mp4") -> str:
    safe = re.sub(r'[\\/*?:"<>|]', "", title)
    safe = safe.strip().replace(" ", "_")[:50]
    return f"{safe}.{ext}"
