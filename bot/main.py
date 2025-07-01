# bot/main.py
import os
import logging
from dotenv import load_dotenv

from telegram.ext import Application, Defaults
from telegram.constants import ParseMode

from .db import engine as db_engine, Base as db_Base
from .models import User, Character, GameSession # Ensure models are imported so Base knows about them
from .handlers import command_handlers, error_handler, player_action_handler # Added player_action_handler
from .character_creation import character_creation_handler # This is a ConversationHandler
from .utils import get_logger
from .gemini_gm import GEMINI_API_KEY # To conditionally add GM handlers

# Set up logging
logger = get_logger(__name__) # Use the utility for consistency

def main() -> None:
    """Start the telegram bot."""
    load_dotenv() # Load environment variables from .env

    # Get Telegram Bot Token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    # Create database tables if they don't exist
    # This imports all models that use Base, so Base.metadata knows about them
    logger.info("Initializing database and creating tables if they don't exist...")
    db_Base.metadata.create_all(bind=db_engine)
    logger.info("Database initialized.")

    # Set default parse mode for messages
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).defaults(defaults).build()

    # Register command handlers
    for handler in command_handlers:
        application.add_handler(handler)

    # Register the character creation conversation handler
    application.add_handler(character_creation_handler)

    # Register GM related handlers only if API key is present
    if GEMINI_API_KEY:
        application.add_handler(player_action_handler)
        logger.info("Gemini GM MessageHandler for player actions registered.")
    else:
        logger.warning("GEMINI_API_KEY not found. GM MessageHandler for player actions will NOT be registered. /explore command will also notify user.")

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting bot polling...")
    application.run_polling()
    logger.info("Bot stopped.")

if __name__ == "__main__":
    # Configure logging for the whole application if not already configured by utils
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler() # Output to console
            # You can add logging.FileHandler("bot.log") here if you want file logging
        ]
    )
    main()
