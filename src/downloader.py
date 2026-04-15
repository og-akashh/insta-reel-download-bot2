import yt_dlp
import asyncio
import os
import requests
from .config import Config
from .utils import logger

class VideoDownloader:
    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        Config.ensure_download_dir()

    def is_url_reachable(self, url: str) -> bool:
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return True

    def _get_ydl_opts(self, output_template: str, is_audio: bool = False):
        if is_audio:
            return {
                "outtmpl": output_template,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": True,
                "retries": 5,
                "fragment_retries": 5,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }
        else:
            return {
                "outtmpl": output_template,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "ignoreerrors": True,
                "retries": 5,
                "fragment_retries": 5,
                "ratelimit": 10000000,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }

    async def download(self, url: str, is_audio: bool = False):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_download, url, is_audio)

    def _sync_download(self, url: str, is_audio: bool = False):
        try:
            if not self.is_url_reachable(url):
                return None, "URL not accessible"

            ydl_opts = self._get_ydl_opts(f"{self.download_path}/%(title)s.%(ext)s", is_audio)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    return None, "No video/audio info"

                file_path = ydl.prepare_filename(info)
                if is_audio:
                    file_path = file_path.rsplit(".", 1)[0] + ".mp3"
                elif not os.path.exists(file_path):
                    file_path = file_path.rsplit(".", 1)[0] + ".mp4"

                if not os.path.exists(file_path):
                    return None, "File not found after download"

                title = info.get("title", "media")
                logger.info(f"Downloaded: {title}")
                return file_path, title

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "login required" in error_msg.lower():
                return None, "Login required (private content)"
            elif "private" in error_msg.lower():
                return None, "Content is private"
            return None, f"Download error: {error_msg[:100]}"
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None, str(e)[:100]
