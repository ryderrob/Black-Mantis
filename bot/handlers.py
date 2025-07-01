# bot/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy.orm import Session

from .db import get_db
from .models import User, Character, GameSession
from .utils import get_logger, format_character_sheet
from .game_logic import handle_roll_command # Import the specific handler
from .localization import _, set_language, get_current_language, SUPPORTED_LANGUAGES # Localization
# from .character_creation import start_character_creation # This will be handled by ConversationHandler entry point

logger = get_logger(__name__)


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows the user to change the language."""
    user = update.effective_user
    if not context.args:
        await update.message.reply_text(
            f"Current language: {get_current_language().upper()}\n"
            f"To change language, use /lang <lang_code> (e.g., /lang ru).\n"
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )
        return

    lang_code = context.args[0].lower()
    if lang_code in SUPPORTED_LANGUAGES:
        set_language(lang_code) # This sets it globally for now
        # Ideally, this would be stored per-user in the database
        # and `set_language` would be called at the beginning of each handler
        # based on `update.effective_user.language_code` or DB preference.
        await update.message.reply_text(f"Language changed to: {lang_code.upper()}")
        logger.info(f"User {user.id} changed language to {lang_code}")
    else:
        await update.message.reply_text(
            f"Unsupported language code: {lang_code}.\n"
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")

    db: Session = next(get_db())
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        new_user = User(id=user.id, username=user.username or user.first_name)
        db.add(new_user)
        db.commit()
        logger.info(f"New user {user.id} ({user.first_name}) added to database.")
    db.close()

    # Note: update.effective_user.language_code could be used here for initial language detection
    # For now, using the globally set language via /lang command or default.
    await update.message.reply_html(
        _("welcome_bot", user_mention=user.mention_html())
    )

async def start_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /startgame command in a group chat."""
    chat = update.effective_chat
    user = update.effective_user

    if not chat.type == "group" and not chat.type == "supergroup":
        await update.message.reply_text(_("startgame_group_only"))
        logger.warning(f"/startgame called by {user.id} in non-group chat {chat.id} ({chat.type})")
        return

    logger.info(f"/startgame called by {user.id} in group chat {chat.id} ({chat.title})")
    db: Session = next(get_db())

    # Ensure the user who typed /startgame is in the User table
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        new_user = User(id=user.id, username=user.username or user.first_name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user) # Ensure we have the latest from DB if concurrent access occurs
        db_user = new_user
        logger.info(f"User {user.id} added to DB via /startgame command.")


    game_session = db.query(GameSession).filter(GameSession.chat_id == chat.id).first()

    if not game_session:
        game_session = GameSession(chat_id=chat.id, is_active=True, current_scene="A new adventure begins in this group!")
        db.add(game_session)
        db.commit()
        db.refresh(game_session)
        logger.info(f"New game session created for chat {chat.id}.")
        await update.message.reply_text(_("new_game_session"))
    elif not game_session.is_active:
        game_session.is_active = True
        # Potentially localize this scene text too if it's shown to users
        game_session.current_scene = "The adventure in The Black Mantis resumes!"
        db.commit()
        logger.info(f"Game session reactivated for chat {chat.id}.")
        await update.message.reply_text(_("game_session_resumed"))
    else:
        logger.info(f"Game session already active for chat {chat.id}.")
        # await update.message.reply_text("A game is already active in this group!") # Maybe too noisy

    # Check if the user has a character
    character = db.query(Character).filter(Character.user_id == user.id).first()
    db.close()

    if character:
        await update.message.reply_text(
            _("welcome_back_character", character_name=character.name)
        )
    else:
        keyboard = [
            [InlineKeyboardButton(_("create_character_button"), callback_data="create_character")],
            # [InlineKeyboardButton("👤 Load Existing Character (Not Implemented)", callback_data="load_character_NYI")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            _("welcome_new_player", user_first_name=user.first_name),
            reply_markup=reply_markup,
        )

async def my_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's character sheet."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested /mycharacter.")

    db: Session = next(get_db())
    character = db.query(Character).join(User).filter(User.id == user_id).first()
    db.close()

    if character:
        sheet = format_character_sheet(character)
        await update.message.reply_text(sheet, parse_mode='Markdown')
    else:
        # Check if they are in a group with an active game to guide them better
        chat_id = update.effective_chat.id
        db_game_session = None
        if update.effective_chat.type in ["group", "supergroup"]:
            db: Session = next(get_db())
            db_game_session = db.query(GameSession).filter(GameSession.chat_id == chat_id, GameSession.is_active == True).first()
            db.close()

        if db_game_session:
             keyboard = [
                [InlineKeyboardButton(_("create_character_button"), callback_data="create_character")],
            ]
             reply_markup = InlineKeyboardMarkup(keyboard)
             await update.message.reply_text(
                _("no_character_prompt_creation_group"),
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(_("no_character_prompt_creation_private"))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


# List of handlers to be imported and used in main.py
# The character_creation_handler is imported separately in main.py as it's a ConversationHandler
command_handlers = [
    CommandHandler("start", start_command),
    CommandHandler("startgame", start_game_command),
    CommandHandler("mycharacter", my_character_command),
    CommandHandler("roll", handle_roll_command), # Using the imported handler directly
    CommandHandler("lang", lang_command), # Added language command
]

# CallbackQueryHandlers that are not part of a ConversationHandler can be listed here
# For now, character creation ones are managed by the ConversationHandler itself.
# Example:
# callback_handlers = [
#    CallbackQueryHandler(some_general_button_handler, pattern="^general_button_")
# ]
# For this project, most callbacks will be inside ConversationHandlers or simple like create_character trigger.
# The 'create_character' callback is the entry point for the ConversationHandler.
# It will be handled by the ConversationHandler itself, which should be registered in main.py.
# No separate CallbackQueryHandler for 'create_character' needed here if it's an entry point.
# However, if /startgame provides the button, that button's callback *is* the entry point.
# The `character_creation_handler` from `character_creation.py` will have its own entry point.
# This means `start_character_creation` is triggered by a callback query with pattern 'create_character'.
# We don't need to register it twice.

# This file will primarily export lists of handlers for main.py to register.
# For ConversationHandlers, they are typically imported and registered directly in main.py.
# For standalone CommandHandlers and CallbackQueryHandlers, they can be grouped here.
all_handlers = command_handlers # Add other handler lists if any (e.g. + callback_handlers)
