import os
from pathlib import Path
from dotenv import load_dotenv

# Get the path to the .env file
env_path = Path(__file__).parent / '.env'

# Load the .env file
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")
    print("EMAIL_HOST_USER:", os.environ.get('EMAIL_HOST_USER', ''))
    print("EMAIL_HOST_PASSWORD:", os.environ.get('EMAIL_HOST_PASSWORD', ''))
else:
    print(f"No .env file found at: {env_path}") 