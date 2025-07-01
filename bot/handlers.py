# bot/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy.orm import Session

from telegram.ext import MessageHandler, filters # Added filters for MessageHandler

from .db import get_db, SessionLocal # Added SessionLocal for direct use if needed
from .models import User, Character, GameSession
from .utils import get_logger, format_character_sheet
from .game_logic import handle_roll_command # Import the specific handler
from .localization import _, set_language, get_current_language, SUPPORTED_LANGUAGES # Localization
from .gemini_gm import generate_gm_response, GEMINI_API_KEY # Import Gemini GM function and API key status
# from .character_creation import start_character_creation # This will be handled by ConversationHandler entry point

logger = get_logger(__name__)


# --- GM Integration Handlers ---
async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /explore command, triggering a GM narration of the current scene."""
    if not GEMINI_API_KEY:
        await update.message.reply_text(_("gemini_fallback_unavailable"))
        return

    user = update.effective_user
    chat = update.effective_chat

    if not chat.type == "group" and not chat.type == "supergroup":
        await update.message.reply_text(_("startgame_group_only")) # Re-use existing key, context is similar
        return

    db_session: SessionLocal = next(get_db())
    try:
        game_session = db_session.query(GameSession).filter(GameSession.chat_id == chat.id, GameSession.is_active == True).first()
        if not game_session:
            await update.message.reply_text(_("explore_no_active_session"))
            return

        player_character = db_session.query(Character).filter(Character.user_id == user.id).first()
        if not player_character:
            await update.message.reply_text(_("explore_no_character"))
            return

        # Notify that GM is thinking
        thinking_message = await update.message.reply_text("The GM ponders the weave of fate...")

        gm_response = await generate_gm_response(chat_id=chat.id, acting_user_id=user.id, is_explore_action=True)

        if thinking_message: # Edit the "thinking" message with the actual response
            await context.bot.edit_message_text(chat_id=chat.id, message_id=thinking_message.message_id, text=gm_response)
        else: # Fallback if somehow thinking_message wasn't sent
            await update.message.reply_text(gm_response)

    finally:
        db_session.close()


async def handle_player_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles regular text messages as player actions in an active game."""
    if not GEMINI_API_KEY:
        # Silently ignore if Gemini is not configured, or reply if direct feedback is preferred
        # logger.debug("Gemini not configured, ignoring potential player action.")
        return

    user = update.effective_user
    chat = update.effective_chat
    message_text = update.message.text

    if not chat.type == "group" and not chat.type == "supergroup":
        return # Player actions are for group chats

    db_session: SessionLocal = next(get_db())
    try:
        game_session = db_session.query(GameSession).filter(GameSession.chat_id == chat.id, GameSession.is_active == True).first()
        if not game_session:
            # logger.debug(f"Player action ignored: No active game session in chat {chat.id}")
            return # No active game

        player_character = db_session.query(Character).filter(Character.user_id == user.id).first()
        if not player_character:
            # logger.debug(f"Player action ignored: User {user.id} has no character in chat {chat.id}")
            return # User has no character

        # Optional: Add a small delay or "GM is thinking" message if responses are slow
        # thinking_message = await update.message.reply_text("The GM considers your action...")

        gm_response = await generate_gm_response(chat_id=chat.id, acting_user_id=user.id, player_action_text=message_text)

        # if thinking_message:
        #    await context.bot.edit_message_text(chat_id=chat.id, message_id=thinking_message.message_id, text=gm_response)
        # else:
        await update.message.reply_text(gm_response)

    finally:
        db_session.close()

# --- End GM Integration Handlers ---


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
    CommandHandler("roll", handle_roll_command),
    CommandHandler("lang", lang_command),
    CommandHandler("explore", explore_command), # Added explore command
]

# MessageHandler for player actions (GM interaction)
# Ensure this handler has a group that doesn't conflict with ConversationHandler if it also uses MessageHandlers.
# A common approach is to use different groups or ensure ConversationHandler entry points are more specific.
# For now, adding it directly. If conflicts arise, adjust handler groups.
# The priority should be such that it doesn't override command handlers.
# Default group is 0. CommandHandlers are typically in group 0.
# ConversationHandler states might also be in group 0.
# To ensure commands are processed first, and then this, it might be fine.
# If it captures text meant for ConversationHandler, we might need to make its filters more specific
# or manage handler groups. For now, `~filters.COMMAND` should prevent it from hijacking commands.
player_action_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.GROUPS, handle_player_action)


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
