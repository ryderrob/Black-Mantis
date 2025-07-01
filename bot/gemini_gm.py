# bot/gemini_gm.py
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

from .utils import get_logger
from .db import get_db, SessionLocal
from .models import GameSession, Character, User
from .localization import _ # For fallback messages

logger = get_logger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash-latest" # Using "latest" is good practice

# Configure the Gemini client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured.")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. Gemini GM features will be disabled.")

# Global model instance (can be None if API key is missing)
gemini_model = None
if GEMINI_API_KEY:
    try:
        gemini_model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Gemini model '{MODEL_NAME}' initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}", exc_info=True)
        gemini_model = None # Ensure it's None if initialization fails


# Safety settings for Gemini - adjust as needed for a fantasy RPG
# Blocking too much might hinder creative storytelling.
# Start with less restrictive and adjust if problematic content arises.
# Refer to Google AI Studio or Gemini API docs for details on these settings.
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# Generation configuration
GENERATION_CONFIG = {
    "temperature": 0.8, # Controls randomness. Higher is more creative.
    "top_p": 0.9,       # Nucleus sampling.
    "top_k": 40,        # Top-k sampling.
    "max_output_tokens": 500, # Max length of the GM's response.
}

MAX_HISTORY_TURNS = 5 # Number of user/model turn pairs to keep in history (total 10 messages)


async def generate_gm_response(chat_id: int, acting_user_id: int, player_action_text: str = None, is_explore_action: bool = False) -> str:
    """
    Generates a response from the Gemini GM based on game context and player action.
    """
    if not gemini_model:
        logger.warning("Gemini model not available. Cannot generate GM response.")
        return _("gemini_fallback_unavailable") # New localization key

    db: SessionLocal = next(get_db())
    try:
        game_session = db.query(GameSession).filter(GameSession.chat_id == chat_id).first()
        if not game_session or not game_session.is_active:
            # This check should ideally be done before calling this function by the handler
            logger.warning(f"Attempted GM response for inactive/non-existent session {chat_id}")
            return _("gm_session_not_active") # New localization key

        # Fetch characters in the current game session
        # This requires characters to be linked to a game_session_id or users linked to characters in the current chat.
        # For now, let's assume we fetch all characters whose users are in the group.
        # This part might need refinement based on how characters are associated with a specific GameSession.
        # A simple way: Get all characters whose user_id is in the list of users who have interacted with this group.
        # A better way: Link Character model to GameSession or have a PlayerInSession model.
        # For now, let's get all characters. This is a simplification.

        # Fetch all characters. In a multi-group bot, you'd filter by characters active in *this* game_session.
        # For this project, we assume User has one Character. We need to find users in the group.
        # Telegram bot library doesn't easily give all users in a group.
        # We'll rely on characters that have interacted or are explicitly part of the session (if we add that link).
        # For now, let's fetch all characters for simplicity of prompt construction, though ideally it'd be session-specific.

        # Simplified: Get all characters for now. This is not ideal for multiple concurrent games.
        # A better approach would be to iterate through users who have interacted in this chat
        # and fetch their characters.
        # For now, we'll fetch all characters in the DB and list them.
        all_characters_in_db = db.query(Character).join(User).all() # Simplified

        # Construct character summaries
        character_summaries = []
        for char in all_characters_in_db: # Ideally, filter for characters in *this* game session
            # TODO: Get localized race/class names for the prompt if possible, or use keys
            char_summary = (
                f"- {char.name} (Race: {char.race}, Class: {char._class}, HP: {char.health}/{char.max_health}, "
                f"Str: {char.strength}, Dex: {char.dexterity}, Int: {char.intelligence})"
            )
            if char.user_id == acting_user_id:
                char_summary += " (Current Actor)"
            character_summaries.append(char_summary)

        characters_prompt_text = "\n".join(character_summaries) if character_summaries else "No adventurers are currently present."

        # Conversation history from GameSession (list of dicts: {'role': 'user'/'model', 'parts': [{'text': '...'}]})
        history = list(game_session.conversation_history or []) # Ensure it's a mutable list

        # System Prompt Construction
        system_prompt_parts = [
            "You are the Game Master (GM) for a text-based fantasy roleplaying game called 'The Black Mantis'.",
            "Your role is to narrate scenes, describe the outcomes of player actions, and drive the story forward.",
            "Maintain a consistent fantasy tone, be descriptive, and engage the players.",
            "Current Game State:",
            f"  Location/Scene: {game_session.current_scene or 'An unknown place'}",
            "  Characters Present:\n" + (characters_prompt_text if characters_prompt_text else "    It seems quiet here... too quiet."),
            "\nInstructions for your response:",
            "- Describe the scene and the immediate consequences of the player's action (if any).",
            "- If it's an 'explore' action, describe the current location and interesting features in more detail.",
            "- Do NOT control player characters directly. Do not state their thoughts, feelings, or actions they haven't taken.",
            "- Do NOT generate dice rolls or specific game mechanics numbers (like damage). The bot handles dice rolls separately.",
            "- Keep responses concise (1-3 paragraphs) unless more detail is contextually required by the player's action.",
            "- End your response with a clear question or a prompt that encourages players to decide their next action (e.g., 'What do you do next?', 'How do you react?', 'Before you lies X and Y, which path do you choose?').",
            "- If the story reaches a natural pause or a new area, you can update the 'Location/Scene' by including a line like: `[SCENE_UPDATE: New Location Name or Description]` at the VERY END of your response. The bot will parse this.",
        ]

        # Add player action to history if it exists
        if player_action_text:
            acting_character = db.query(Character).filter(Character.user_id == acting_user_id).first()
            actor_name = acting_character.name if acting_character else f"Player_{acting_user_id}"
            history.append({'role': 'user', 'parts': [{'text': f"{actor_name} (Player Action): {player_action_text}"}]})
        elif is_explore_action:
             history.append({'role': 'user', 'parts': [{'text': "System (Player Action): The players decide to explore the area."}]})


        # Construct messages for Gemini API (system prompt + history)
        # The Gemini API prefers the system instruction to be part of the model constructor or a specific field.
        # For `generate_content_async`, the history itself forms the prompt.
        # The first message in history can act as a system-like instruction if not using the dedicated system_instruction param.
        # Let's construct full_prompt_messages including a system-like intro if needed.

        # For gemini-1.5-flash, system_instruction is a specific parameter for genai.GenerativeModel.
        # We can pass it during model initialization or per request.
        # For now, let's prepend system instructions to the history for simplicity if not using system_instruction directly.
        # The `genai.GenerativeModel` can take `system_instruction`. Let's try to use that.

        model_for_request = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction="\n".join(system_prompt_parts),
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG
        )

        # Trim history to not exceed token limits (simplistic trimming)
        # Each turn is a user message + model response. So MAX_HISTORY_TURNS * 2 messages.
        if len(history) > MAX_HISTORY_TURNS * 2:
            history = history[-(MAX_HISTORY_TURNS * 2):]

        logger.debug(f"Gemini History for chat {chat_id}: {history}")
        newline_char = '\n'
        logger.debug(f"Gemini System Prompt for chat {chat_id}: {newline_char.join(system_prompt_parts)}")


        response = await model_for_request.generate_content_async(history) # Pass the history

        gm_reply_text = ""
        if response.parts:
            gm_reply_text = "".join(part.text for part in response.parts if part.text) # Handle potential non-text parts if any
        else: # Fallback if parts is empty but text might exist (older API versions or specific cases)
             gm_reply_text = response.text if hasattr(response, 'text') and response.text else ""


        if not gm_reply_text.strip():
            logger.warning(f"Gemini returned empty response for chat {chat_id}. History: {history}")
            # Check for prompt feedback if available
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                logger.warning(f"Gemini response blocked. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}")
                # More specific fallback based on block reason can be added
                return _("gemini_response_blocked") # New localization key
            return _("gemini_empty_response") # New localization key

        # Check for SCENE_UPDATE directive
        scene_update_tag = "[SCENE_UPDATE:"
        if scene_update_tag in gm_reply_text:
            try:
                # Extract new scene: everything between "[SCENE_UPDATE:" and "]"
                start_index = gm_reply_text.rfind(scene_update_tag) + len(scene_update_tag)
                end_index = gm_reply_text.rfind("]", start_index)
                if end_index > start_index:
                    new_scene_description = gm_reply_text[start_index:end_index].strip()
                    game_session.current_scene = new_scene_description
                    # Remove the tag from the reply text shown to user
                    gm_reply_text = gm_reply_text[:gm_reply_text.rfind(scene_update_tag)].strip()
                    logger.info(f"Chat {chat_id}: Scene updated by GM to: {new_scene_description}")
            except Exception as e_parse:
                logger.error(f"Error parsing SCENE_UPDATE tag: {e_parse}", exc_info=True)
                # Don't fail the whole response, just log it.

        # Update history with GM's response
        history.append({'role': 'model', 'parts': [{'text': gm_reply_text}]})

        # Trim history again before saving
        if len(history) > MAX_HISTORY_TURNS * 2:
            history = history[-(MAX_HISTORY_TURNS * 2):]

        game_session.conversation_history = history
        db.commit()

        logger.info(f"Gemini GM response generated for chat {chat_id}.")
        return gm_reply_text.strip()

    except ResourceExhausted as e:
        logger.error(f"Gemini API rate limit hit for chat {chat_id}: {e}", exc_info=True)
        return _("gemini_rate_limit_fallback") # New localization key
    except GoogleAPIError as e:
        logger.error(f"Gemini API error for chat {chat_id}: {e}", exc_info=True)
        return _("gemini_api_error_fallback") # New localization key
    except Exception as e:
        logger.error(f"Unexpected error in generate_gm_response for chat {chat_id}: {e}", exc_info=True)
        return _("gemini_unexpected_error_fallback") # New localization key
    finally:
        db.close()

# Placeholder for localization keys to be added in localization.py:
# "gemini_fallback_unavailable": "The GM's magical link is currently severed. Please try again later."
# "gm_session_not_active": "There is no active game session here for the GM to respond to."
# "gemini_rate_limit_fallback": "The ancient magics are strained and need a moment to recover (Rate limit reached). Please try your action again shortly."
# "gemini_api_error_fallback": "A flicker in the arcane energies disrupts the GM's focus. (API Error). Please try again."
# "gemini_unexpected_error_fallback": "An unforeseen magical disturbance has occurred! The GM is momentarily unavailable. Please try again."
# "gemini_empty_response": "The GM ponders your action but remains silent for now... Perhaps try rephrasing or a different action?"
# "gemini_response_blocked": "The GM's thoughts were mysteriously blocked. Perhaps try a different approach?"
