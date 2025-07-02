# The Black Mantis - Telegram RPG Bot

A text-based roleplaying game bot for Telegram, powering the adventures in "The Black Mantis".

## Features (Initial)

*   Character Creation
*   Character Management
*   Dice Rolling
*   Group-based game sessions

## Setup

There are two ways to set up the bot:

### Option 1: Using the Setup Script (Recommended for Linux/macOS)

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd telegram_rpg_bot # Or your chosen directory name
    ```

2.  **Run the setup script:**
    ```bash
    ./setup.sh
    ```
    This script will:
    *   Check for Python 3.
    *   Create a Python virtual environment (named `venv`).
    *   Install required dependencies from `requirements.txt`.
    *   Copy `.env_example` to `.env` if `.env` doesn't exist.
    *   Guide you to edit the `.env` file.

3.  **Activate the virtual environment (if not already active from the script's guidance):**
    ```bash
    source venv/bin/activate
    ```

4.  **Configure Environment Variables:**
    *   Open the `.env` file created by the script (or manually).
    *   **Add your Telegram Bot Token:**
        *   Get a token by talking to [BotFather](https://t.me/BotFather) on Telegram.
        *   Set the `TELEGRAM_BOT_TOKEN` variable.
    *   **Add your Google Gemini API Key:**
        *   Go to [Google AI Studio](https://makersuite.google.com/app/apikey) to create an API key.
        *   Set the `GEMINI_API_KEY` variable in the `.env` file.
        ```env
        TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_TELEGRAM_BOT_TOKEN"
        DATABASE_URL="sqlite:///./rpg_bot.db" # You can change this if you prefer another DB location
        GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
        ```
    *   **These steps are crucial for the bot to connect to Telegram and for the GM features to work.**

5.  **Run the bot:**
    ```bash
    python -m bot.main
    ```

### Option 2: Manual Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd telegram_rpg_bot # Or your chosen directory name
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv  # Ensure you use python3
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Copy `.env_example` to `.env`:
        ```bash
        cp .env_example .env
        ```
    *   Open `.env` and add your Telegram Bot Token as described in step 4 of "Option 1".

5.  **Run the bot:**
    ```bash
    python -m bot.main
    ```

## Project Structure

```
telegram_rpg_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point, bot setup
│   ├── db.py                   # Database setup, SQLAlchemy session
│   ├── models.py               # SQLAlchemy ORM models
│   ├── handlers.py             # Command and callback query handlers
│   ├── character_creation.py   # Logic for character creation flow
│   ├── game_logic.py           # Core game mechanics (dice rolling, etc.)
│   ├── utils.py                # Utility functions
│   └── config.py               # Game configuration (races, classes, etc.)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (ignored by git)
├── .env_example                # Example environment variables
└── README.md                   # This file
```

## How to Play

### Available Commands

Here's a list of commands you can use with The Black Mantis RPG Bot:

*   **`/start`**: Displays a welcome message from the bot.
*   **`/startgame`**:
    *   Initiates a new game session in the current group chat if one isn't active.
    *   Reactivates an inactive game session.
    *   Prompts you to create a character if you don't have one for the session.
    *   *Must be used in a group chat.*
*   **`/mycharacter`**: Shows your current character's sheet, including stats, race, class, etc. If you don't have a character, it will guide you to create one (usually via `/startgame`).
*   **`/roll <XdY[+Z]>`**: Rolls dice based on standard dice notation.
    *   Examples: `/roll d20`, `/roll 2d6`, `/roll 1d10+3`, `/roll 3d8-1`.
*   **`/lang <language_code>`**: Changes the bot's display language.
    *   Examples: `/lang en` (for English), `/lang ru` (for Russian).
    *   *Currently, this setting is global for the bot instance.*
*   **`/explore`**: (Requires Gemini API Key) Asks the AI Game Master to provide a detailed description of the current scene or location. This helps you understand your surroundings better.
    *   *Only works in an active game session where you have a character.*
*   **`/cancel`**: Used during multi-step processes like character creation to cancel the current operation.

### AI Game Master (GM) Interaction

*   When a game is active (initiated by `/startgame`) and you have a character, simply typing a message in the group chat (that is not a command) will be interpreted as your character's action.
*   The AI Game Master, powered by Google Gemini, will read your action, consider the game context (current scene, other characters, recent events), and narrate the outcome and the evolving story.
*   The GM will often end its narration with a question or a prompt for players to decide what to do next.

## AI Game Master (Gemini Integration)

This bot uses Google's Gemini API to provide dynamic Game Master capabilities. To use these features, you must:
1.  Obtain a Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Set this key as the `GEMINI_API_KEY` environment variable in your `.env` file.

If the `GEMINI_API_KEY` is not provided or is invalid, the GM-related features (`/explore` and responding to player actions) will be disabled, and the bot will inform you.

## Language Support

*   The bot currently supports English (en) and Russian (ru).
*   The default language is English.
*   You can switch the language using the `/lang` command.

Further instructions will be provided by the bot.
```
