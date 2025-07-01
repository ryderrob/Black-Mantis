# bot/config.py

# Initial game configuration

# Localized names and descriptions for races and classes.
# Keys for names: name_en, name_ru
# Keys for descriptions: desc_en, desc_ru
# The functions in character_creation.py and utils.py will use get_current_language()
# to pick the appropriate field.

AVAILABLE_RACES = {
    "human": {
        "name_en": "Human", "desc_en": "Versatile and adaptable.",
        "name_ru": "Человек", "desc_ru": "Универсальны и адаптивны."
    },
    "elf": {
        "name_en": "Elf", "desc_en": "Graceful and attuned to nature.",
        "name_ru": "Эльф", "desc_ru": "Изящны и созвучны природе."
    },
    "dwarf": {
        "name_en": "Dwarf", "desc_en": "Sturdy and skilled craftsmen.",
        "name_ru": "Дворф", "desc_ru": "Крепкие и искусные ремесленники."
    },
    "orc": {
        "name_en": "Orc", "desc_en": "Strong and formidable warriors.",
        "name_ru": "Орк", "desc_ru": "Сильные и грозные воины."
    },
}

AVAILABLE_CLASSES = {
    "warrior": {
        "name_en": "Warrior", "desc_en": "Master of combat, strong and resilient.",
        "name_ru": "Воин", "desc_ru": "Мастер боя, сильный и выносливый."
    },
    "mage": {
        "name_en": "Mage", "desc_en": "Wielder of arcane energies.",
        "name_ru": "Маг", "desc_ru": "Повелитель тайных энергий."
    },
    "rogue": {
        "name_en": "Rogue", "desc_en": "Stealthy and skilled in subterfuge.",
        "name_ru": "Разбойник", "desc_ru": "Скрытный и искусный в уловках."
    },
    "cleric": {
        "name_en": "Cleric", "desc_en": "Divine agent, healer, and protector.",
        "name_ru": "Клирик", "desc_ru": "Божественный агент, целитель и защитник."
    },
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
