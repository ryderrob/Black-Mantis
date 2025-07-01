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

from .localization import _, get_current_language # For translations
from .config import AVAILABLE_RACES, AVAILABLE_CLASSES # To get localized race/class names

def format_character_sheet(character) -> str:
    """Formats character information into a readable string using localization."""
    if not character:
        return _("no_character_yet") # Assuming this key exists or will be added

    # Get localized race and class names
    # This assumes that character.race and character._class store the keys (e.g., "human", "warrior")
    # And that config.py will be updated to provide localized names.
    lang = get_current_language()

    race_details = AVAILABLE_RACES.get(character.race.lower(), {})
    localized_race_name = race_details.get(f"name_{lang}", race_details.get("name_en", character.race.capitalize()))

    class_details = AVAILABLE_CLASSES.get(character._class.lower(), {})
    localized_class_name = class_details.get(f"name_{lang}", class_details.get("name_en", character._class.capitalize()))


    sheet = (
        f"{_('character_sheet_title', character_name=character.name)}\n"
        f"------------------------------------\n"
        f"**{_('race_label')}:** {localized_race_name}\n"
        f"**{_('class_label')}:** {localized_class_name}\n"
        f"------------------------------------\n"
        f"**{_('hp_label')}:** {character.health}/{character.max_health}\n"
        f"**{_('mp_label')}:** {character.mana}/{character.max_mana}\n"
        f"------------------------------------\n"
        f"**{_('attributes_label')}:**\n"
        f"  {_('strength_label')}: {character.strength}\n"
        f"  {_('dexterity_label')}: {character.dexterity}\n"
        f"  {_('constitution_label')}: {character.constitution}\n"
        f"  {_('intelligence_label')}: {character.intelligence}\n"
        f"  {_('wisdom_label')}: {character.wisdom}\n"
        f"  {_('charisma_label')}: {character.charisma}\n"
        f"------------------------------------\n"
        f"**{_('location_label')}:** {character.location}\n"
        # f"**{_('inventory_label')}:** {character.inventory if character.inventory else _('inventory_empty')}\n"
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
