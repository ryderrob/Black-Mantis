#!/bin/bash

echo "Starting The Black Mantis RPG Bot Setup..."
echo "=========================================="

# --- Check for Python 3 ---
echo -n "Checking for Python 3... "
if ! command -v python3 &> /dev/null
then
    echo "FAIL"
    echo "Python 3 could not be found. Please install Python 3 and try again."
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo "OK ($PYTHON_VERSION)"
fi

# --- Virtual Environment ---
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists."
    read -p "Do you want to skip recreating it? (y/N): " skip_venv
    if [[ "$skip_venv" =~ ^[Yy]$ ]]; then
        echo "Skipping virtual environment creation."
    else
        echo "Removing existing virtual environment '$VENV_DIR'..."
        rm -rf "$VENV_DIR"
        echo "Creating virtual environment '$VENV_DIR'..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment. Please check your Python 3 installation."
            exit 1
        fi
    fi
else
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please check your Python 3 installation."
        exit 1
    fi
fi

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Try activating it manually: source $VENV_DIR/bin/activate"
    # We can continue as pip install might still work if user activates manually later
fi
echo "Virtual environment active (or attempted)."
echo ""

# --- Install Dependencies ---
echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies. Please check requirements.txt and ensure pip is working."
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "WARNING: requirements.txt not found. Skipping dependency installation."
fi
echo ""

# --- Environment File ---
ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env_example"

if [ -f "$ENV_FILE" ]; then
    echo "$ENV_FILE already exists. Skipping creation from $ENV_EXAMPLE_FILE."
    echo "Please ensure your $ENV_FILE is correctly configured with your TELEGRAM_BOT_TOKEN."
else
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        echo "Copying $ENV_EXAMPLE_FILE to $ENV_FILE..."
        cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
        echo "$ENV_FILE created successfully."
        echo "IMPORTANT: You MUST edit the '$ENV_FILE' file and add your TELEGRAM_BOT_TOKEN."
        echo "You can get a token by talking to @BotFather on Telegram."
    else
        echo "WARNING: $ENV_EXAMPLE_FILE not found. Cannot create $ENV_FILE."
        echo "Please create an '$ENV_FILE' manually with your TELEGRAM_BOT_TOKEN and other settings."
    fi
fi
echo ""

# --- Final Instructions ---
echo "=========================================="
echo "Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. If you haven't already, activate the virtual environment:"
echo "   source $VENV_DIR/bin/activate"
echo "2. CRITICAL: Edit the '.env' file and set your TELEGRAM_BOT_TOKEN."
echo "   Example: TELEGRAM_BOT_TOKEN=\"123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11\""
echo "3. Run the bot using:"
echo "   python -m bot.main"
echo ""
echo "Enjoy playing The Black Mantis!"
echo "=========================================="

# Note: The script doesn't keep the venv active after it finishes.
# The user needs to activate it in their current shell session.
