# 🎥 Telegram Media Downloader Bot

A powerful Telegram bot that downloads **Instagram Reels, Posts, Stories, IGTV** and **YouTube Shorts, Videos, Audio** with mandatory channel join verification and inline buttons.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## ✨ Features

- 📸 **Instagram** – Reels, Posts, Stories, IGTV
- 🎬 **YouTube** – Shorts, Normal Videos, Audio extraction (mp3)
- 🔐 **Channel Join Verification** – Users must join required channels before using the bot
- 🧩 **Inline Buttons** – Join buttons on start, share & support buttons after each download
- ⏰ **Auto‑Cleanup** – Files deleted from server and chat after 20 minutes
- 📋 **Full Command Menu** – `/start`, `/help`, `/about`, `/reset`
- 🐳 **Docker Ready** – Deploy on Render (free tier) with one click
- ⚡ **Asynchronous & Fast** – Handles multiple users concurrently

## 🚀 Deploy on Render (Free)

### One‑Click Deploy

Click the button above, then:

1. Connect your GitHub repository.
2. Add the required environment variables (see below).
3. Click **Apply**.

### Manual Deploy

1. Fork this repository.
2. On [Render](https://render.com), create a **New Web Service**.
3. Connect your repo – Render will auto‑detect the `Dockerfile`.
4. Add the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your bot token from @BotFather | `123456:ABC-DEF` |
| `REQUIRED_CHANNELS` | Comma-separated `channel_id,invite_link` (use `;` to separate multiple) | `-100123456789,https://t.me/joinchat/abc; -100987654321,https://t.me/joinchat/xyz` |
| `OWNER_LINK` | Your Telegram profile link | `https://t.me/yourusername` |
| `SUPPORT_CHANNEL_LINK` | Link to support group/channel | `https://t.me/support` |
| `DELETE_AFTER_MINUTES` | Auto‑delete after (minutes) | `20` |
| `MAX_FILE_SIZE_MB` | Max file size (MB) | `50` |
| `LOG_LEVEL` | Logging level | `INFO` |

5. Click **Create Web Service**.
6. Your bot will be live in a few minutes.

> **Keep it alive for free** – Use [UptimeRobot](https://uptimerobot.com) to ping `https://your-bot.onrender.com/health` every 5 minutes (prevents idle spin‑down).

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & join verification (if channels configured) |
| `/help` | Show help and supported media types |
| `/about` | Bot info and links |
| `/reset` | Reset verification (if you need to re‑join channels) |

## 🔧 How It Works

1. **Verification** – On `/start`, the bot shows inline buttons to join required channels. User must click **"Yes, I joined"** before any download.
2. **Download** – Send any supported link (Instagram Reel/Post/Story, YouTube Shorts/Video). For audio, add `#audio` or `audio` in the message.
3. **After Download** – The bot sends the media along with three optional buttons: **Owner**, **Support**, **Share Bot**.
4. **Auto‑Cleanup** – All downloaded files are deleted from the server and the chat message after 20 minutes (configurable).

## 📁 Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/telegram-media-bot
cd telegram-media-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required)
# Ubuntu: sudo apt install ffmpeg
# Mac: brew install ffmpeg
# Windows: download from ffmpeg.org

# Create .env file
cp .env.example .env
# Edit .env with your BOT_TOKEN and channel links

# Run the bot
python -m src.bot
