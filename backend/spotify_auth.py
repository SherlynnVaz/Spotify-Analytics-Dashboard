import os

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


SCOPES = (
    "user-read-private "
    "user-top-read "
    "user-read-recently-played "
    "playlist-read-private"
)


def get_spotify_oauth():

    return SpotifyOAuth(
        client_id=os.getenv(
            "SPOTIFY_CLIENT_ID"
        ),

        client_secret=os.getenv(
            "SPOTIFY_CLIENT_SECRET"
        ),

        redirect_uri=os.getenv(
            "SPOTIFY_REDIRECT_URI"
        ),

        scope=SCOPES,

        cache_path=None,
    )


def get_spotify_client(code):

    oauth = get_spotify_oauth()

    token_info = oauth.get_access_token(
        code,
        as_dict=True
    )

    return spotipy.Spotify(
        auth=token_info["access_token"],
        retries=0
    )