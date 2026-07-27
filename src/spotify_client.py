import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI
)

SCOPES = (
    "user-top-read "
    "user-read-recently-played "
    "playlist-read-private "
    "playlist-read-collaborative"
)


def get_spotify_client():
    """
    Returns an authenticated Spotify client.
    """

    # Check if credentials exist
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        print("=" * 60)
        print("Spotify credentials not found!")
        print("=" * 60)
        print()
        print("Setup Instructions:")
        print("1. Copy '.env.example' to '.env'")
        print("2. Create a Spotify Developer App")
        print("3. Add your Spotify Client ID")
        print("4. Add your Spotify Client Secret")
        print("5. Set the Redirect URI to:")
        print("   http://127.0.0.1:8888/callback")
        print()
        print("Then run the project again.")
        sys.exit(1)

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPES
            )
        )

        return sp

    except Exception as e:
        print("=" * 60)
        print("Failed to authenticate with Spotify.")
        print("=" * 60)
        print(f"Error: {e}")


        sys.exit(1)