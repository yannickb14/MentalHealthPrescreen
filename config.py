import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY")

def validate_config():
    """
    Validates that necessary environment variables are set.
    """
    if not BACKBOARD_API_KEY:
        print("Warning: API_KEY is not set.")

if __name__ == "__main__":
    validate_config()
    print("Configuration loaded successfully.")
