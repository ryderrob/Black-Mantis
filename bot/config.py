# bot/config.py

# Initial game configuration
# This can be expanded or moved to a database/JSON file later for more dynamic configuration.

AVAILABLE_RACES = {
    "human": {"name": "Human", "description": "Versatile and adaptable."},
    "elf": {"name": "Elf", "description": "Graceful and attuned to nature."},
    "dwarf": {"name": "Dwarf", "description": "Sturdy and skilled craftsmen."},
    "orc": {"name": "Orc", "description": "Strong and formidable warriors."},
}

AVAILABLE_CLASSES = {
    "warrior": {"name": "Warrior", "description": "Master of combat, strong and resilient."},
    "mage": {"name": "Mage", "description": "Wielder of arcane energies."},
    "rogue": {"name": "Rogue", "description": "Stealthy and skilled in subterfuge."},
    "cleric": {"name": "Cleric", "description": "Divine agent, healer, and protector."},
}

# Base stats - these can be adjusted by race/class modifiers
BASE_STATS = {
    "health": 50,
    "max_health": 50,
    "mana": 30,
    "max_mana": 30,
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}

# Example modifiers (can be more complex)
# These are simple additions; a more robust system might use multipliers or specific formulas
RACE_STAT_MODIFIERS = {
    "human": {"constitution": 2, "charisma": 1},
    "elf": {"dexterity": 2, "intelligence": 1},
    "dwarf": {"constitution": 2, "strength": 1, "charisma": -1},
    "orc": {"strength": 2, "constitution": 1, "intelligence": -1},
}

CLASS_STAT_MODIFIERS = {
    "warrior": {"strength": 2, "constitution": 1, "health": 20, "max_health": 20},
    "mage": {"intelligence": 2, "wisdom": 1, "mana": 20, "max_mana": 20},
    "rogue": {"dexterity": 2, "intelligence": 1},
    "cleric": {"wisdom": 2, "charisma": 1, "mana": 10, "max_mana": 10},
}

# Default starting location
DEFAULT_STARTING_LOCATION = "Tavern"

# Conversation states for character creation
(
    CHOOSE_NAME,
    CHOOSE_RACE,
    CHOOSE_CLASS,
    CONFIRM_CREATION,
    CHARACTER_CREATION_COMPLETE,
) = range(5)
