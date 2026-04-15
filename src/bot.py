import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from .config import Config
from .handlers import (
    start, help_command, about_command, reset_command,
    handle_message, verify_callback, error_handler
)
from .utils import setup_logging, logger

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = Config.PORT
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

def main():
    Config.validate()
    setup_logging(Config.LOG_LEVEL)

    # Start health server thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    application = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("reset", reset_command))
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Callback for verification
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_joined"))
    # Error handler
    application.add_error_handler(error_handler)

    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message", "callback_query"], drop_pending_updates=True)

if __name__ == "__main__":
    main()
