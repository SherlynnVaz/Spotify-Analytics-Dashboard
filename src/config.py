import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Validate credentials
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    raise ValueError(
        "Missing Spotify credentials. Check your .env file."
    )