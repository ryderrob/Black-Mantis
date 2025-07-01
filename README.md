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
    *   Add your Telegram Bot Token:
        *   Get a token by talking to [BotFather](https://t.me/BotFather) on Telegram.
        *   Replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` (or ensure the line is correctly set) with your actual token.
        ```env
        TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_TELEGRAM_BOT_TOKEN"
        DATABASE_URL="sqlite:///./rpg_bot.db" # You can change this if you prefer another DB location
        ```
    *   **This step is crucial for the bot to connect to Telegram.**

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

## How to Play (Initial Commands)

*   `/startgame` - Initiates a new game session in the group chat or helps you join an existing one.
*   `/createcharacter` - (Usually triggered via `/startgame`) Starts the character creation process.
*   `/mycharacter` - Displays your current character's sheet.
*   `/roll <XdY[+Z]>` - Rolls dice (e.g., `/roll d20`, `/roll 2d6+3`).
*   `/lang <language_code>` - Changes the bot's language (e.g., `/lang ru` for Russian, `/lang en` for English). Currently, this is a global setting for the bot instance.

## Language Support

*   The bot currently supports English (en) and Russian (ru).
*   The default language is English.
*   You can switch the language using the `/lang` command.

Further instructions will be provided by the bot.
```
