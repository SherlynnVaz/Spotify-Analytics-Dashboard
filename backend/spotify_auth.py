import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=(
            "user-top-read "
            "user-read-recently-played "
            "user-read-email "
            "playlist-read-private"
        )
    )


def get_spotify_client(code):
    oauth = get_spotify_oauth()

    token_info = oauth.get_access_token(
        code,
        as_dict=True
    )

    return spotipy.Spotify(
        auth=token_info["access_token"]
    )