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

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPES
        )
    )