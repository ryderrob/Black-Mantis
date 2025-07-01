# bot/character_creation.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from sqlalchemy.orm import Session

from .db import get_db, SessionLocal
from .models import User, Character, GameSession
from .utils import get_logger, calculate_initial_stats, format_character_sheet
from .config import (
    AVAILABLE_RACES, AVAILABLE_CLASSES, DEFAULT_STARTING_LOCATION,
    CHOOSE_NAME, CHOOSE_RACE, CHOOSE_CLASS, CONFIRM_CREATION, CHARACTER_CREATION_COMPLETE
)

logger = get_logger(__name__)

# --- Helper Functions ---
def get_user_from_context(context: ContextTypes.DEFAULT_TYPE, telegram_user_id: int) -> User | None:
    """Fetches or creates a User DB entry."""
    db: Session = next(get_db())
    user = db.query(User).filter(User.id == telegram_user_id).first()
    if not user:
        # This part might need to be called explicitly when a user first interacts,
        # or ensure user is created before character creation starts.
        # For now, let's assume the user is created if they try to make a character.
        logger.warning(f"User {telegram_user_id} not found in DB during character creation. This should ideally not happen here.")
        # user = User(id=telegram_user_id, username=context.user_data.get("telegram_username", "Unknown"))
        # db.add(user)
        # db.commit()
        # db.refresh(user)
        # logger.info(f"Created new user {telegram_user_id} during character creation.")
        return None # Or handle user creation more gracefully elsewhere
    return user

async def start_character_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the character creation conversation."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    db: Session = next(get_db())
    # Ensure user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        db_user = User(id=user_id, username=update.effective_user.username or update.effective_user.first_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User {user_id} created at the start of character creation.")

    existing_character = db.query(Character).filter(Character.user_id == user_id).first()
    db.close()

    if existing_character:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"You already have a character: {existing_character.name}.\n"
                 f"If you want to create a new one, you might need a command to delete the old one first (not yet implemented)."
        ) # TODO: Add a /deletecharacter command or similar
        return ConversationHandler.END

    context.user_data['character_info'] = {}
    context.user_data['telegram_username'] = update.effective_user.username or update.effective_user.first_name

    await update.callback_query.answer() # Answer the button press
    await update.callback_query.edit_message_text( # Edit the message that had the button
        text="Let's create your character! First, what is your character's name?"
    )
    return CHOOSE_NAME

async def choose_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles character name input."""
    name = update.message.text.strip()
    if not name or len(name) < 2 or len(name) > 30:
        await update.message.reply_text("Please enter a valid name (2-30 characters).")
        return CHOOSE_NAME

    context.user_data['character_info']['name'] = name
    logger.info(f"User {update.effective_user.id} chose name: {name}")

    keyboard = [
        [InlineKeyboardButton(details["name"], callback_data=f"race_{race_key}") for race_key, details in AVAILABLE_RACES.items()]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Great, {name}! Now, choose your character's race:", reply_markup=reply_markup)
    return CHOOSE_RACE

async def choose_race(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles race selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    race_key = query.data.split('_')[1]

    if race_key not in AVAILABLE_RACES:
        await query.edit_message_text("Invalid race selected. Please try again.")
        # Resend race options if needed, or handle error
        return CHOOSE_RACE

    context.user_data['character_info']['race'] = race_key
    logger.info(f"User {update.effective_user.id} chose race: {race_key}")

    keyboard = [
        [InlineKeyboardButton(details["name"], callback_data=f"class_{class_key}") for class_key, details in AVAILABLE_CLASSES.items()]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"You chose {AVAILABLE_RACES[race_key]['name']}. Now, select your class:",
        reply_markup=reply_markup
    )
    return CHOOSE_CLASS

async def choose_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles class selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    class_key = query.data.split('_')[1]

    if class_key not in AVAILABLE_CLASSES:
        await query.edit_message_text("Invalid class selected. Please try again.")
        # Resend class options
        return CHOOSE_CLASS

    context.user_data['character_info']['class'] = class_key
    logger.info(f"User {update.effective_user.id} chose class: {class_key}")

    # All info gathered, calculate stats and show summary for confirmation
    char_info = context.user_data['character_info']
    stats = calculate_initial_stats(char_info['race'], char_info['class'])
    context.user_data['character_info']['stats'] = stats

    summary_text = (
        f"**Character Summary:**\n"
        f"Name: {char_info['name']}\n"
        f"Race: {AVAILABLE_RACES[char_info['race']]['name']}\n"
        f"Class: {AVAILABLE_CLASSES[char_info['class']]['name']}\n\n"
        f"**Initial Stats:**\n"
        f"HP: {stats['max_health']}/{stats['max_health']}\n"
        f"MP: {stats['max_mana']}/{stats['max_mana']}\n"
        f"Strength: {stats['strength']}\n"
        f"Dexterity: {stats['dexterity']}\n"
        f"Constitution: {stats['constitution']}\n"
        f"Intelligence: {stats['intelligence']}\n"
        f"Wisdom: {stats['wisdom']}\n"
        f"Charisma: {stats['charisma']}\n\n"
        f"Does this look correct?"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ Looks Good!", callback_data="confirm_creation_yes"),
            InlineKeyboardButton("❌ Start Over", callback_data="confirm_creation_no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
    return CONFIRM_CREATION


async def confirm_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles confirmation of character details and saves the character."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "confirm_creation_yes":
        char_info = context.user_data['character_info']
        stats = char_info['stats']

        db: Session = next(get_db())
        try:
            # Ensure user exists (should be guaranteed by start_character_creation or handler entry)
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                # This case should ideally be prevented earlier.
                logger.error(f"User {user_id} not found when trying to save character. Aborting.")
                await query.edit_message_text("Error: User not found. Please try /startgame again.")
                db.close()
                return ConversationHandler.END

            new_character = Character(
                user_id=user_id,
                name=char_info['name'],
                race=char_info['race'],
                _class=char_info['class'],
                health=stats['health'],
                max_health=stats['max_health'],
                mana=stats['mana'],
                max_mana=stats['max_mana'],
                strength=stats['strength'],
                dexterity=stats['dexterity'],
                constitution=stats['constitution'],
                intelligence=stats['intelligence'],
                wisdom=stats['wisdom'],
                charisma=stats['charisma'],
                inventory=[], # Start with an empty inventory
                location=DEFAULT_STARTING_LOCATION
            )
            db.add(new_character)
            db.commit()
            db.refresh(new_character)
            logger.info(f"Character {new_character.name} created for user {user_id}.")

            final_message = (
                f"🎉 Character '{new_character.name}' created successfully! 🎉\n\n"
                f"{format_character_sheet(new_character)}\n\n"
                "You are ready to begin your adventure in The Black Mantis! Use /mycharacter to see your sheet again."
            )
            await query.edit_message_text(text=final_message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error saving character for user {user_id}: {e}", exc_info=True)
            await query.edit_message_text("An error occurred while saving your character. Please try again.")
            # Potentially roll back if partial save, though SQLAlchemy handles this with commit
        finally:
            db.close()
            context.user_data.pop('character_info', None) # Clean up user_data
            return ConversationHandler.END

    elif query.data == "confirm_creation_no":
        # Restart the conversation by asking for name again
        context.user_data.pop('character_info', None) # Clear previous attempt
        await query.edit_message_text(text="Okay, let's start over. What is your character's name?")
        return CHOOSE_NAME

    return CONFIRM_CREATION # Should not happen if buttons are defined correctly


async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the character creation process."""
    user = update.effective_user
    logger.info(f"User {user.id} canceled character creation.")
    context.user_data.pop('character_info', None)

    # Check if the cancel was triggered by a command or a callback query
    if update.message:
        await update.message.reply_text("Character creation cancelled.")
    elif update.callback_query:
        await update.callback_query.answer("Character creation cancelled.")
        await update.callback_query.edit_message_text("Character creation cancelled.")

    return ConversationHandler.END

# ConversationHandler for character creation
# This will be added to the application in main.py
character_creation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_character_creation, pattern='^create_character$')],
    states={
        CHOOSE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_name)],
        CHOOSE_RACE: [CallbackQueryHandler(choose_race, pattern='^race_')],
        CHOOSE_CLASS: [CallbackQueryHandler(choose_class, pattern='^class_')],
        CONFIRM_CREATION: [CallbackQueryHandler(confirm_creation, pattern='^confirm_creation_')],
    },
    fallbacks=[
        CommandHandler('cancel', cancel_creation),
        CallbackQueryHandler(cancel_creation, pattern='^cancel_creation$') # Optional: a cancel button
    ],
    map_to_parent={ # If this conversation is nested, how to return
        ConversationHandler.END: ConversationHandler.END # Or specific state if part of larger flow
    }
)
