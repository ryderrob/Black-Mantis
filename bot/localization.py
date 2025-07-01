# bot/localization.py

# Simple dictionary-based localization for now.
# We can expand this or move to gettext for more complex needs.

# --- Default Language ---
DEFAULT_LANG = "en"
SUPPORTED_LANGUAGES = ["en", "ru"]

# --- Translations ---
# Structure: translations[lang_code][string_key]
translations = {
    "en": {
        # General
        "welcome_bot": "Hi {user_mention}! Welcome to The Black Mantis, your friendly RPG Bot. Use /startgame in a group chat to begin an adventure!",
        "startgame_group_only": "The /startgame command can only be used in group chats.",
        "new_game_session": "A new game session for The Black Mantis has started in this group! Let the adventure begin!",
        "game_session_resumed": "The game session for The Black Mantis in this group is now active again!",
        "welcome_back_character": "Welcome back to The Black Mantis, {character_name}! The game is afoot. You can view your character with /mycharacter.",
        "welcome_new_player": "Welcome, {user_first_name}! To join the adventure in The Black Mantis, you need a character. Would you like to create one?",
        "create_character_button": "✨ Create New Character",
        "character_sheet_title": "📜 **Character Sheet: {character_name}** 📜",
        "race_label": "Race",
        "class_label": "Class",
        "hp_label": "HP",
        "mp_label": "MP",
        "attributes_label": "Attributes",
        "strength_label": "💪 Strength",
        "dexterity_label": "🤸 Dexterity",
        "constitution_label": "맷 Constitution",
        "intelligence_label": "🧠 Intelligence",
        "wisdom_label": "🤔 Wisdom",
        "charisma_label": "🗣️ Charisma",
        "location_label": "Location",
        "inventory_label": "Inventory", # Not fully implemented yet
        "inventory_empty": "Empty", # Not fully implemented yet
        "no_character_yet": "You don't have a character yet.",
        "no_character_prompt_creation_group": "You don't have a character yet for this game session. Would you like to create one?",
        "no_character_prompt_creation_private": "You don't have a character yet. Use /startgame in a group chat where you want to play, then create your character.",
        "roll_usage_prompt": "Please specify what dice to roll (e.g., /roll d20, /roll 2d6+3).",
        "roll_invalid_notation": "Invalid dice notation: '{dice_notation}'.\nUse format like `d20`, `2d6`, or `3d8+5`.",
        "roll_result_single_no_mod": "{user_first_name} rolled {dice_notation}: **{total}**",
        "roll_result_multi_no_mod": "{user_first_name} rolled {dice_notation}: ({rolls_str}) = **{total}**",
        "roll_result_with_mod": "{user_first_name} rolled {dice_notation}: ({rolls_str}){modifier_str} = **{total}**",

        # Character Creation
        "char_creation_already_exists": "You already have a character: {character_name}.\nIf you want to create a new one, you might need a command to delete the old one first (not yet implemented).",
        "char_creation_start_prompt": "Let's create your character! First, what is your character's name?",
        "char_creation_invalid_name": "Please enter a valid name (2-30 characters).",
        "char_creation_race_prompt": "Great, {name}! Now, choose your character's race:",
        "char_creation_invalid_race": "Invalid race selected. Please try again.",
        "char_creation_class_prompt": "You chose {race_name}. Now, select your class:",
        "char_creation_invalid_class": "Invalid class selected. Please try again.",
        "char_creation_summary_title": "**Character Summary:**",
        "char_creation_summary_name": "Name",
        "char_creation_summary_race": "Race",
        "char_creation_summary_class": "Class",
        "char_creation_summary_stats_title": "**Initial Stats:**",
        "char_creation_confirm_prompt": "Does this look correct?",
        "char_creation_confirm_yes": "✅ Looks Good!",
        "char_creation_confirm_no": "❌ Start Over",
        "char_creation_user_not_found_error": "Error: User not found. Please try /startgame again.",
        "char_creation_success": "🎉 Character '{character_name}' created successfully! 🎉\n\n{character_sheet}\n\nYou are ready to begin your adventure in The Black Mantis! Use /mycharacter to see your sheet again.",
        "char_creation_save_error": "An error occurred while saving your character. Please try again.",
        "char_creation_restart": "Okay, let's start over. What is your character's name?",
        "char_creation_cancelled": "Character creation cancelled.",

        # Races (name, description) - will be moved/integrated with config.py
        "race_human_name": "Human", "race_human_desc": "Versatile and adaptable.",
        "race_elf_name": "Elf", "race_elf_desc": "Graceful and attuned to nature.",
        "race_dwarf_name": "Dwarf", "race_dwarf_desc": "Sturdy and skilled craftsmen.",
        "race_orc_name": "Orc", "race_orc_desc": "Strong and formidable warriors.",

        # Classes (name, description) - will be moved/integrated with config.py
        "class_warrior_name": "Warrior", "class_warrior_desc": "Master of combat, strong and resilient.",
        "class_mage_name": "Mage", "class_mage_desc": "Wielder of arcane energies.",
        "class_rogue_name": "Rogue", "class_rogue_desc": "Stealthy and skilled in subterfuge.",
        "class_cleric_name": "Cleric", "class_cleric_desc": "Divine agent, healer, and protector.",
    },
    "ru": {
        # General
        "welcome_bot": "Привет, {user_mention}! Добро пожаловать в The Black Mantis, ваш дружелюбный RPG бот! Используйте /startgame в групповом чате, чтобы начать приключение!",
        "startgame_group_only": "Команда /startgame может быть использована только в групповых чатах.",
        "new_game_session": "Новая игровая сессия The Black Mantis началась в этой группе! Да начнется приключение!",
        "game_session_resumed": "Игровая сессия The Black Mantis в этой группе снова активна!",
        "welcome_back_character": "С возвращением в The Black Mantis, {character_name}! Игра началась. Вы можете посмотреть своего персонажа с помощью /mycharacter.",
        "welcome_new_player": "Добро пожаловать, {user_first_name}! Чтобы присоединиться к приключению в The Black Mantis, вам нужен персонаж. Хотите создать его?",
        "create_character_button": "✨ Создать нового персонажа",
        "character_sheet_title": "📜 **Лист персонажа: {character_name}** 📜",
        "race_label": "Раса",
        "class_label": "Класс",
        "hp_label": "ОЗ", # Очки Здоровья
        "mp_label": "ОМ", # Очки Маны
        "attributes_label": "Атрибуты",
        "strength_label": "💪 Сила",
        "dexterity_label": "🤸 Ловкость",
        "constitution_label": "맷 Телосложение",
        "intelligence_label": "🧠 Интеллект",
        "wisdom_label": "🤔 Мудрость",
        "charisma_label": "🗣️ Харизма",
        "location_label": "Локация",
        "inventory_label": "Инвентарь",
        "inventory_empty": "Пусто",
        "no_character_yet": "У вас еще нет персонажа.",
        "no_character_prompt_creation_group": "У вас еще нет персонажа для этой игровой сессии. Хотите создать его?",
        "no_character_prompt_creation_private": "У вас еще нет персонажа. Используйте /startgame в групповом чате, где вы хотите играть, затем создайте своего персонажа.",
        "roll_usage_prompt": "Пожалуйста, укажите, какие кости бросить (например, /roll d20, /roll 2d6+3).",
        "roll_invalid_notation": "Неверная нотация костей: '{dice_notation}'.\nИспользуйте формат вроде `d20`, `2d6` или `3d8+5`.",
        "roll_result_single_no_mod": "{user_first_name} бросил(а) {dice_notation}: **{total}**",
        "roll_result_multi_no_mod": "{user_first_name} бросил(а) {dice_notation}: ({rolls_str}) = **{total}**",
        "roll_result_with_mod": "{user_first_name} бросил(а) {dice_notation}: ({rolls_str}){modifier_str} = **{total}**",

        # Character Creation
        "char_creation_already_exists": "У вас уже есть персонаж: {character_name}.\nЕсли вы хотите создать нового, вам может понадобиться команда для удаления старого (пока не реализовано).",
        "char_creation_start_prompt": "Давайте создадим вашего персонажа! Сначала, как зовут вашего персонажа?",
        "char_creation_invalid_name": "Пожалуйста, введите корректное имя (2-30 символов).",
        "char_creation_race_prompt": "Отлично, {name}! Теперь выберите расу вашего персонажа:",
        "char_creation_invalid_race": "Выбрана неверная раса. Пожалуйста, попробуйте снова.",
        "char_creation_class_prompt": "Вы выбрали {race_name}. Теперь выберите ваш класс:",
        "char_creation_invalid_class": "Выбран неверный класс. Пожалуйста, попробуйте снова.",
        "char_creation_summary_title": "**Обзор персонажа:**",
        "char_creation_summary_name": "Имя",
        "char_creation_summary_race": "Раса",
        "char_creation_summary_class": "Класс",
        "char_creation_summary_stats_title": "**Начальные параметры:**",
        "char_creation_confirm_prompt": "Все верно?",
        "char_creation_confirm_yes": "✅ Все верно!",
        "char_creation_confirm_no": "❌ Начать сначала",
        "char_creation_user_not_found_error": "Ошибка: Пользователь не найден. Пожалуйста, попробуйте /startgame снова.",
        "char_creation_success": "🎉 Персонаж '{character_name}' успешно создан! 🎉\n\n{character_sheet}\n\nВы готовы начать свое приключение в The Black Mantis! Используйте /mycharacter, чтобы снова увидеть свой лист персонажа.",
        "char_creation_save_error": "Произошла ошибка при сохранении вашего персонажа. Пожалуйста, попробуйте снова.",
        "char_creation_restart": "Хорошо, давайте начнем сначала. Как зовут вашего персонажа?",
        "char_creation_cancelled": "Создание персонажа отменено.",

        # Races (name, description)
        "race_human_name": "Человек", "race_human_desc": "Универсальны и адаптивны.",
        "race_elf_name": "Эльф", "race_elf_desc": "Изящны и созвучны природе.",
        "race_dwarf_name": "Дворф", "race_dwarf_desc": "Крепкие и искусные ремесленники.",
        "race_orc_name": "Орк", "race_orc_desc": "Сильные и грозные воины.",

        # Classes (name, description)
        "class_warrior_name": "Воин", "class_warrior_desc": "Мастер боя, сильный и выносливый.",
        "class_mage_name": "Маг", "class_mage_desc": "Повелитель тайных энергий.",
        "class_rogue_name": "Разбойник", "class_rogue_desc": "Скрытный и искусный в уловках.",
        "class_cleric_name": "Клирик", "class_cleric_desc": "Божественный агент, целитель и защитник.",
    }
}

# Store current language (can be per-user later)
# For now, a global variable for simplicity in this step.
# In a real scenario, this would be fetched from user settings in the DB.
_current_lang = DEFAULT_LANG

def set_language(lang_code: str):
    """Sets the current language for the bot's responses."""
    global _current_lang
    if lang_code in SUPPORTED_LANGUAGES:
        _current_lang = lang_code
    else:
        _current_lang = DEFAULT_LANG

def get_current_language() -> str:
    """Gets the currently set language."""
    return _current_lang

def get_translation(key: str, lang: str = None, **kwargs) -> str:
    """
    Fetches a translation for a given key in the specified language.
    If lang is not provided, uses the current global language.
    If a key is not found, returns the key itself.
    kwargs can be used for string formatting.
    """
    if lang is None:
        lang = _current_lang

    try:
        translation = translations[lang][key]
        if kwargs:
            return translation.format(**kwargs)
        return translation
    except KeyError:
        # Fallback to default language if key not found in specified lang
        if lang != DEFAULT_LANG:
            try:
                translation = translations[DEFAULT_LANG][key]
                if kwargs:
                    return translation.format(**kwargs)
                return translation
            except KeyError:
                pass # Key not found in default lang either
        # If key is not found anywhere, return the key itself or a placeholder
        return f"[{key}]" # Or just key

# Alias for convenience
_ = get_translation

# Example usage:
# from .localization import _, set_language
# set_language("ru")
# print(_("welcome_bot", user_mention="TestUser"))
# set_language("en")
# print(_("welcome_bot", user_mention="TestUser"))
# print(_("some_missing_key"))
