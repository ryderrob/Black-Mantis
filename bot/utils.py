# bot/utils.py
import logging

# Basic logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_logger(name: str):
    """Returns a logger instance for a given module name."""
    return logging.getLogger(name)


def format_character_sheet(character) -> str:
    """Formats character information into a readable string."""
    if not character:
        return "No character found."

    sheet = (
        f"📜 **Character Sheet: {character.name}** 📜\n"
        f"------------------------------------\n"
        f"**Race:** {character.race.capitalize()}\n"
        f"**Class:** {character._class.capitalize()}\n"
        f"------------------------------------\n"
        f"**HP:** {character.health}/{character.max_health}\n"
        f"**MP:** {character.mana}/{character.max_mana}\n"
        f"------------------------------------\n"
        f"**Attributes:**\n"
        f"  💪 Strength: {character.strength}\n"
        f"  🤸 Dexterity: {character.dexterity}\n"
        f"  맷 Constitution: {character.constitution}\n"
        f"  🧠 Intelligence: {character.intelligence}\n"
        f"  🤔 Wisdom: {character.wisdom}\n"
        f"  🗣️ Charisma: {character.charisma}\n"
        f"------------------------------------\n"
        f"**Location:** {character.location}\n"
        # f"**Inventory:** {character.inventory if character.inventory else 'Empty'}\n" # Add when inventory is implemented
    )
    return sheet


def calculate_initial_stats(race: str, char_class: str) -> dict:
    """
    Calculates initial character stats based on race and class.
    """
    from .config import BASE_STATS, RACE_STAT_MODIFIERS, CLASS_STAT_MODIFIERS

    stats = BASE_STATS.copy()

    # Apply race modifiers
    if race_mods := RACE_STAT_MODIFIERS.get(race.lower()):
        for stat, modifier in race_mods.items():
            if stat in stats:
                stats[stat] += modifier
            elif stat == "health" or stat == "max_health": # ensure health/max_health are updated together
                stats["health"] += modifier
                stats["max_health"] += modifier
            elif stat == "mana" or stat == "max_mana": # ensure mana/max_mana are updated together
                stats["mana"] += modifier
                stats["max_mana"] += modifier


    # Apply class modifiers
    if class_mods := CLASS_STAT_MODIFIERS.get(char_class.lower()):
        for stat, modifier in class_mods.items():
            if stat in stats:
                stats[stat] += modifier
            elif stat == "health" or stat == "max_health":
                stats["health"] += modifier
                stats["max_health"] += modifier
            elif stat == "mana" or stat == "max_mana":
                stats["mana"] += modifier
                stats["max_mana"] += modifier

    # Ensure health and mana don't exceed max values if modified directly
    stats["health"] = min(stats["health"], stats["max_health"])
    stats["mana"] = min(stats["mana"], stats["max_mana"])

    # Ensure stats don't go below a minimum (e.g., 1) if desired
    for key, value in stats.items():
        if key not in ["health", "max_health", "mana", "max_mana"]: # Don't apply floor to HP/MP which can be 0
            if value < 1:
                stats[key] = 1
        elif key in ["max_health", "max_mana"]: # Max values should be at least 1
             if value < 1:
                stats[key] = 1


    return stats
