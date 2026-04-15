import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from .downloader import VideoDownloader
from .utils import is_supported_url, delete_file_async, logger
from .config import Config
from .verification import is_user_verified, set_user_verified, clear_verification

downloader = VideoDownloader()

# --- Helper to build channel buttons for verification ---
def get_join_buttons():
    keyboard = []
    for ch in Config.REQUIRED_CHANNELS:
        keyboard.append([InlineKeyboardButton(f"📢 Join {ch['identifier']}", url=ch['invite_link'])])
    keyboard.append([InlineKeyboardButton("✅ Yes, I joined", callback_data="verify_joined")])
    return InlineKeyboardMarkup(keyboard)

# --- After download buttons (not mandatory) ---
def get_after_download_buttons():
    keyboard = [
        [
            InlineKeyboardButton("👑 Owner", url=Config.OWNER_LINK),
            InlineKeyboardButton("💬 Support", url=Config.SUPPORT_CHANNEL_LINK)
        ],
        [InlineKeyboardButton("📤 Share Bot", switch_inline_query="")]  # Opens share dialog
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Start command handler with verification check ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name

    if not Config.REQUIRED_CHANNELS:
        # No channels to verify, just welcome
        await update.message.reply_text(
            f"🎉 Welcome {user}!\n\n"
            "Send me any Instagram Reel, Post, Story, or YouTube video link.\n"
            "I'll download it for you!\n\n"
            "Commands:\n/help - Show help\n/about - About this bot"
        )
        return

    if is_user_verified(chat_id):
        await update.message.reply_text(
            f"✅ Welcome back {user}!\nSend me any link to download."
        )
    else:
        # Show join verification message
        msg = (
            f"🔐 *Verification Required* {user}\n\n"
            "Please join the following channels before using this bot:\n\n"
        )
        for idx, ch in enumerate(Config.REQUIRED_CHANNELS, 1):
            msg += f"{idx}. {ch['identifier']}\n"
        msg += "\nAfter joining, click the button below."
        await update.message.reply_text(
            msg,
            reply_markup=get_join_buttons(),
            parse_mode="Markdown"
        )

# --- Handle verification callback ---
async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name

    if query.data == "verify_joined":
        # For simplicity, we trust the user. In production, you can check membership via bot API.
        # To actually check, you'd need bot to be admin in those channels.
        set_user_verified(chat_id)
        await query.edit_message_text(
            f"✅ Verification successful {user}!\n\n"
            "Now you can send me Instagram or YouTube links."
        )
    else:
        await query.edit_message_text("Invalid option.")

# --- Help command ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "Send me any of these links:\n"
        "• Instagram Reel / Post / Story / IGTV\n"
        "• YouTube Shorts / Video\n"
        "• Audio from YouTube (coming soon)\n\n"
        "The bot will download and send the media.\n"
        "All files are automatically deleted after 20 minutes.\n\n"
        "Commands:\n"
        "/start - Welcome\n"
        "/help - This message\n"
        "/about - About the bot\n"
        "/reset - Reset verification (if needed)",
        parse_mode="Markdown"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Telegram Media Downloader Bot*\n\n"
        "Version 2.0\n"
        "Supports Instagram and YouTube media.\n"
        "Developed with ❤️\n\n"
        f"Owner: [Link]({Config.OWNER_LINK})\n"
        f"Support: [Channel]({Config.SUPPORT_CHANNEL_LINK})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clear_verification(chat_id)
    await update.message.reply_text("Verification reset. Please use /start again to re-verify.")

# --- Main message handler with verification gate ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text.strip()

    # Check if user is verified (if channels are required)
    if Config.REQUIRED_CHANNELS and not is_user_verified(chat_id):
        await update.message.reply_text(
            "⚠️ You need to verify by joining our channels first.\n"
            "Please type /start and follow the instructions."
        )
        return

    if not is_supported_url(url):
        await update.message.reply_text(
            "❌ Unsupported link.\n\n"
            "Send me:\n"
            "- Instagram Reel / Post / Story\n"
            "- YouTube Shorts / Video"
        )
        return

    status_msg = await update.message.reply_text("⏳ Downloading... Please wait.")

    # Check if audio requested? For simplicity, you can detect "audio" in command.
    # We'll default to video unless user says "audio" in message.
    is_audio = "audio" in url.lower() or "#audio" in url.lower()
    file_path, title = await downloader.download(url, is_audio=is_audio)

    if not file_path:
        await status_msg.edit_text(f"❌ Download failed: {title}")
        return

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        await status_msg.edit_text(f"❌ File too large ({file_size_mb:.1f} MB). Max: {Config.MAX_FILE_SIZE_MB} MB")
        os.remove(file_path)
        return

    try:
        # Determine media type: audio or video
        if file_path.endswith(".mp3"):
            with open(file_path, "rb") as audio_file:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_file,
                    caption=f"🎵 Downloaded: {title}\n\n⏰ Auto-delete in {Config.DELETE_AFTER_MINUTES} min.",
                    reply_markup=get_after_download_buttons()
                )
        else:
            with open(file_path, "rb") as video_file:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=f"✅ Downloaded: {title}\n\n⏰ Auto-delete in {Config.DELETE_AFTER_MINUTES} min.",
                    supports_streaming=True,
                    reply_markup=get_after_download_buttons()
                )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Failed to send: {e}")
        os.remove(file_path)
        return

    # Schedule file deletion
    asyncio.create_task(delete_file_async(file_path, Config.DELETE_AFTER_MINUTES * 60))

    # Optional: schedule message deletion (needs job_queue)
    if context.job_queue and update.message:
        context.job_queue.run_once(
            delete_chat_message,
            Config.DELETE_AFTER_MINUTES * 60,
            data={"chat_id": chat_id, "message_id": update.message.message_id + 1}
        )

async def delete_chat_message(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    try:
        await context.bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ An error occurred. Please try again later."
        )
