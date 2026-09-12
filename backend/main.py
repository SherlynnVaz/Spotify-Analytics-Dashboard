from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.spotify_auth import get_spotify_oauth
import spotipy


app = FastAPI()


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Temporary in-memory storage for the Spotify token.
# This is fine for our local development version.
spotify_token = None


def get_authenticated_spotify():
    if not spotify_token:
        return None

    return spotipy.Spotify(
        auth=spotify_token["access_token"]
    )


@app.get("/")
def root():
    return {
        "message": "Spotify Analytics API is running"
    }


# --------------------------------------------------
# SPOTIFY LOGIN
# --------------------------------------------------

@app.get("/login")
def login():
    oauth = get_spotify_oauth()

    authorization_url = oauth.get_authorize_url()

    return RedirectResponse(
        url=authorization_url
    )


# --------------------------------------------------
# SPOTIFY CALLBACK
# --------------------------------------------------
@app.get("/callback")
def callback(
    code: str | None = None,
    error: str | None = None
):
    global spotify_token

    if error:
        return {
            "message": "Spotify authorization failed",
            "error": error
        }

    if not code:
        return {
            "message": "No authorization code received"
        }

    try:
        oauth = get_spotify_oauth()

        token_info = oauth.get_access_token(
            code,
            as_dict=True
        )

        spotify_token = token_info

        spotify = spotipy.Spotify(
            auth=token_info["access_token"]
        )

        user = spotify.current_user()

        print(
            f"Spotify login successful: {user.get('display_name')}"
        )

        return RedirectResponse(
            url="http://localhost:5173/"
        )

    except Exception as e:
        print("SPOTIFY AUTH ERROR:", repr(e))

        return {
            "message": "Spotify authorization failed",
            "error": str(e)
        }

# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------

@app.get("/me")
def current_user():
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "authenticated": False
            }

        user = spotify.current_user()

        return {
            "authenticated": True,
            "user": {
                "id": user.get("id"),
                "display_name": user.get("display_name"),
                "email": user.get("email"),
                "image_url": (
                    user["images"][0]["url"]
                    if user.get("images")
                    else None
                )
            }
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# --------------------------------------------------
# TOP TRACKS
# --------------------------------------------------

@app.get("/top-tracks")
def top_tracks():
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify.current_user_top_tracks(
            limit=20,
            time_range="medium_term"
        )

        tracks = []

        for item in results["items"]:
            tracks.append({
                "name": item["name"],
                "artist": item["artists"][0]["name"],
                "album": item["album"]["name"],
                "duration_ms": item["duration_ms"],
                "spotify_url": item["external_urls"]["spotify"],
                "image_url": (
                    item["album"]["images"][0]["url"]
                    if item["album"].get("images")
                    else None
                )
            })

        return {
            "total": len(tracks),
            "tracks": tracks
        }

    except Exception as e:
        print("TOP TRACKS ERROR:", repr(e))

        return {
            "error": str(e)
        }


# --------------------------------------------------
# TOP ARTISTS
# --------------------------------------------------

@app.get("/top-artists")
def top_artists():
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify.current_user_top_artists(
            limit=20,
            time_range="medium_term"
        )

        artists = []

        for item in results["items"]:
            artists.append({
                "name": item["name"],
                "spotify_url": item["external_urls"]["spotify"],
                "image_url": (
                    item["images"][0]["url"]
                    if item.get("images")
                    else None
                )
            })

        return {
            "total": len(artists),
            "artists": artists
        }

    except Exception as e:
        print("TOP ARTISTS ERROR:", repr(e))

        return {
            "error": str(e)
        }


# --------------------------------------------------
# RECENTLY PLAYED
# --------------------------------------------------

@app.get("/recently-played")
def recently_played():
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify.current_user_recently_played(
            limit=20
        )

        tracks = []

        for item in results["items"]:
            track = item["track"]

            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "played_at": item["played_at"],
                "duration_ms": track["duration_ms"],
                "spotify_url": track["external_urls"]["spotify"],
                "image_url": (
                    track["album"]["images"][0]["url"]
                    if track["album"].get("images")
                    else None
                )
            })

        return {
            "total": len(tracks),
            "recently_played": tracks
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# --------------------------------------------------
# PLAYLISTS
# --------------------------------------------------

@app.get("/playlists")
def playlists():
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify.current_user_playlists(
            limit=50
        )

        playlists = []

        for item in results["items"]:
            playlists.append({
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description"),
                "tracks_total": item["items"]["total"],
                "spotify_url": item["external_urls"]["spotify"],
                "image_url": (
                    item["images"][0]["url"]
                    if item["images"]
                    else None
                )
            })

        return {
            "total": len(playlists),
            "playlists": playlists
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# --------------------------------------------------
# PLAYLIST TRACKS
# --------------------------------------------------

@app.get("/playlist-tracks")
def playlist_tracks(playlist_id: str):
    try:
        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify._get(
            f"playlists/{playlist_id}/items",
            limit=50
        )

        tracks = []

        for item in results.get("items", []):
            track = item.get("item")

            if not track:
                continue

            if track.get("type") != "track":
                continue

            tracks.append({
                "name": track.get("name"),
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "duration_ms": track.get("duration_ms"),
                "spotify_url": track["external_urls"]["spotify"],
                "image_url": (
                    track["album"]["images"][0]["url"]
                    if track["album"].get("images")
                    else None
                )
            })

        return {
            "total": len(tracks),
            "tracks": tracks
        }

    except Exception as e:
        print("PLAYLIST ERROR:", repr(e))

        return {
            "error": str(e)
        }