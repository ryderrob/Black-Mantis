# bot/game_logic.py
import random
import re
from .utils import get_logger

logger = get_logger(__name__)

def parse_dice_roll(dice_notation: str) -> tuple[int, int, int] | None:
    """
    Parses dice notation string like "XdY[+Z]" or "dY[+Z]".
    Returns a tuple (num_dice, sides, modifier) or None if invalid.
    """
    match = re.fullmatch(r"(\d*)d(\d+)([\+\-]\d+)?", dice_notation.lower())
    if not match:
        return None

    num_dice_str, sides_str, modifier_str = match.groups()

    num_dice = int(num_dice_str) if num_dice_str else 1
    sides = int(sides_str)
    modifier = int(modifier_str) if modifier_str else 0

    if num_dice <= 0 or num_dice > 100: # Prevent excessive rolls
        logger.warning(f"Invalid number of dice: {num_dice}")
        return None
    if sides <= 1 or sides > 1000: # Prevent invalid or overly large dice
        logger.warning(f"Invalid number of sides: {sides}")
        return None
    if abs(modifier) > 1000: # Prevent overly large modifiers
        logger.warning(f"Invalid modifier: {modifier}")
        return None

    return num_dice, sides, modifier


def roll_dice(num_dice: int, sides: int, modifier: int = 0) -> tuple[list[int], int]:
    """
    Rolls dice and returns the list of individual rolls and the total sum.
    """
    if num_dice <= 0 or sides <= 0:
        return [], 0

    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    return rolls, total


async def handle_roll_command(update, context) -> None:
    """Handles the /roll command."""
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Please specify what dice to roll (e.g., /roll d20, /roll 2d6+3).")
        return

    dice_notation = "".join(context.args)
    parsed_roll = parse_dice_roll(dice_notation)

    if not parsed_roll:
        await update.message.reply_text(
            f"Invalid dice notation: '{dice_notation}'.\n"
            "Use format like `d20`, `2d6`, or `3d8+5`."
        )
        return

    num_dice, sides, modifier = parsed_roll
    rolls, total = roll_dice(num_dice, sides, modifier)

    rolls_str = " + ".join(map(str, rolls))
    modifier_str = ""
    if modifier > 0:
        modifier_str = f" + {modifier}"
    elif modifier < 0:
        modifier_str = f" - {abs(modifier)}"

    if num_dice == 1 and not modifier_str: # e.g. d20
        result_text = f"{user.first_name} rolled {dice_notation}: **{total}**"
    elif num_dice > 1 and not modifier_str: # e.g. 2d6
        result_text = f"{user.first_name} rolled {dice_notation}: ({rolls_str}) = **{total}**"
    else: # e.g. 2d6+3 or d20-1
        result_text = f"{user.first_name} rolled {dice_notation}: ({rolls_str}){modifier_str} = **{total}**"

    await update.message.reply_text(result_text, parse_mode='Markdown')
    logger.info(f"User {user.id} ({user.first_name}) rolled {dice_notation}: {rolls} + {modifier} = {total}")

# Future game logic functions can be added here:
# - Combat mechanics
# - Skill checks
# - NPC interactions
# - Quest progression
# - etc.
