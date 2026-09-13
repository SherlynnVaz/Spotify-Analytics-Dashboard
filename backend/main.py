from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import secrets
import time
from pathlib import Path
import os

import pandas as pd
import requests
import spotipy

from starlette.middleware.sessions import SessionMiddleware

from backend.spotify_auth import get_spotify_oauth


# --------------------------------------------------
# APP SETUP
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# SESSION CONFIGURATION
# --------------------------------------------------

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "local-development-secret-change-me"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False,
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

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


# --------------------------------------------------
# PROJECT PATHS / SESSION STORAGE
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Temporary in-memory session storage.
# Suitable for local development.
spotify_sessions = {}

artwork_cache = {}


# --------------------------------------------------
# SESSION HELPERS
# --------------------------------------------------

def get_session_id(request: Request):
    return request.session.get("session_id")


def get_authenticated_spotify(request: Request):

    session_id = get_session_id(request)

    if not session_id:
        return None

    session_data = spotify_sessions.get(session_id)

    if not session_data:
        return None

    # --------------------------------------------------
    # REFRESH ACCESS TOKEN IF NECESSARY
    # --------------------------------------------------

    expires_at = session_data.get(
        "expires_at",
        0
    )

    if time.time() >= expires_at - 60:

        refresh_token = session_data.get(
            "refresh_token"
        )

        if not refresh_token:
            return None

        try:

            oauth = get_spotify_oauth()

            new_token = (
                oauth.refresh_access_token(
                    refresh_token
                )
            )

            session_data["access_token"] = (
                new_token["access_token"]
            )

            session_data["expires_at"] = (
                new_token.get(
                    "expires_at",
                    int(time.time()) + 3600
                )
            )

            if new_token.get("refresh_token"):

                session_data["refresh_token"] = (
                    new_token["refresh_token"]
                )

        except Exception as error:

            print(
                "TOKEN REFRESH ERROR:",
                repr(error)
            )

            return None

    return spotipy.Spotify(
        auth=session_data["access_token"],
        retries=0
    )


# --------------------------------------------------
# ARTWORK
# --------------------------------------------------

def spotify_artwork_url(
    item_type,
    item_id
):

    cache_key = f"{item_type}:{item_id}"

    if cache_key in artwork_cache:
        return artwork_cache[cache_key]

    try:

        response = requests.get(
            "https://open.spotify.com/oembed",
            params={
                "url": (
                    f"https://open.spotify.com/"
                    f"{item_type}/{item_id}"
                )
            },
            timeout=4,
        )

        response.raise_for_status()

        artwork_url = (
            response.json()
            .get("thumbnail_url")
        )

        artwork_cache[cache_key] = artwork_url

        return artwork_url

    except Exception as error:

        print(
            "ARTWORK LOOKUP ERROR:",
            repr(error)
        )

        return None


def spotify_artist_image_url(spotify, artist_id):

    if not artist_id:
        return None

    cache_key = f"artist-image:{artist_id}"

    if cache_key in artwork_cache:
        return artwork_cache[cache_key]

    try:
        images = spotify.artist(artist_id).get("images", [])
        image_url = images[0].get("url") if images else None
        artwork_cache[cache_key] = image_url
        return image_url
    except Exception as error:
        print(
            "ARTIST IMAGE LOOKUP ERROR:",
            repr(error)
        )
        return None


@app.get("/artwork/{item_type}/{item_id}")
def artwork(
    item_type: str,
    item_id: str
):

    if item_type not in {
        "track",
        "artist"
    }:
        return {
            "error": "Unsupported artwork type"
        }

    artwork_url = spotify_artwork_url(
        item_type,
        item_id
    )

    if not artwork_url:
        return {
            "error": "Artwork unavailable"
        }

    return RedirectResponse(
        url=artwork_url
    )


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Spotify Analytics API is running"
    }


# --------------------------------------------------
# SPOTIFY LOGIN
# --------------------------------------------------

@app.get("/login")
def login(request: Request):

    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)

    request.session["oauth_state"] = state

    oauth = get_spotify_oauth()

    authorization_url = (
        oauth.get_authorize_url(
            state=state
        )
    )

    return RedirectResponse(
        url=authorization_url
    )


# --------------------------------------------------
# SPOTIFY CALLBACK
# --------------------------------------------------

@app.get("/callback")
def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None
):

    # Spotify rejected authorization
    if error:

        return {
            "message": "Spotify authorization failed",
            "error": error
        }

    # No authorization code
    if not code:

        return {
            "message": "No authorization code received"
        }

    # --------------------------------------------------
    # VERIFY OAUTH STATE
    # --------------------------------------------------

    expected_state = request.session.get(
        "oauth_state"
    )

    if (
        not expected_state
        or state != expected_state
    ):

        return {
            "message": "Invalid OAuth state"
        }

    try:

        # --------------------------------------------------
        # EXCHANGE CODE FOR TOKEN
        # --------------------------------------------------

        oauth = get_spotify_oauth()

        token_info = oauth.get_access_token(
            code,
            as_dict=True
        )

        # --------------------------------------------------
        # CREATE USER SESSION
        # --------------------------------------------------

        session_id = secrets.token_urlsafe(32)

        request.session["session_id"] = session_id

        spotify_sessions[session_id] = {

            "access_token": (
                token_info["access_token"]
            ),

            "refresh_token": (
                token_info.get(
                    "refresh_token"
                )
            ),

            "expires_at": (
                token_info.get(
                    "expires_at",
                    int(time.time()) + 3600
                )
            ),

            "user": None,
        }

        # --------------------------------------------------
        # GET SPOTIFY USER
        # --------------------------------------------------

        spotify = spotipy.Spotify(
            auth=token_info["access_token"],
            retries=0
        )

        try:

            user = spotify.current_user()

            spotify_sessions[
                session_id
            ]["user"] = {

                "id": user.get("id"),

                "display_name": (
                    user.get(
                        "display_name"
                    )
                ),

                "image_url": (
                    user["images"][0]["url"]
                    if user.get("images")
                    else None
                ),
            }

            print(
                "Spotify login successful:",
                spotify_sessions[
                    session_id
                ]["user"]["display_name"]
            )

        except Exception as profile_error:

            print(
                "SPOTIFY PROFILE LOOKUP ERROR:",
                repr(profile_error)
            )

            spotify_sessions[
                session_id
            ]["user"] = {

                "id": None,

                "display_name": (
                    "Spotify listener"
                ),

                "image_url": None,
            }

        # --------------------------------------------------
        # REMOVE TEMPORARY OAUTH STATE
        # --------------------------------------------------

        request.session.pop(
            "oauth_state",
            None
        )

        # --------------------------------------------------
        # RETURN TO FRONTEND
        # --------------------------------------------------

        return RedirectResponse(
            url="http://127.0.0.1:5173/"
        )

    except Exception as error:

        print(
            "SPOTIFY AUTH ERROR:",
            repr(error)
        )

        return {
            "message": "Spotify authorization failed",
            "error": str(error)
        }


# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------

@app.get("/me")
def current_user(
    request: Request
):

    session_id = get_session_id(
        request
    )

    if not session_id:

        return {
            "authenticated": False
        }

    session_data = spotify_sessions.get(
        session_id
    )

    if not session_data:

        return {
            "authenticated": False
        }

    # User information already stored
    if session_data.get("user"):

        return {
            "authenticated": True,
            "user": session_data["user"]
        }

    # Otherwise try Spotify
    spotify = get_authenticated_spotify(
        request
    )

    if not spotify:

        return {
            "authenticated": False
        }

    try:

        user = spotify.current_user()

        user_data = {

            "id": user.get("id"),

            "display_name": (
                user.get(
                    "display_name"
                )
            ),

            "image_url": (
                user["images"][0]["url"]
                if user.get("images")
                else None
            ),
        }

        session_data["user"] = user_data

        return {
            "authenticated": True,
            "user": user_data
        }

    except Exception as error:

        print(
            "CURRENT USER ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.post("/logout")
def logout(
    request: Request
):

    session_id = request.session.get(
        "session_id"
    )

    # Remove this user's Spotify session
    if session_id:

        spotify_sessions.pop(
            session_id,
            None
        )

    # Remove browser session
    request.session.clear()

    return {
        "logged_out": True
    }


# --------------------------------------------------
# TOP TRACKS
# --------------------------------------------------

@app.get("/top-tracks")
def top_tracks(
    request: Request,
    time_range: str = "medium_term"
):

    if time_range not in {
        "short_term",
        "medium_term",
        "long_term"
    }:

        time_range = "medium_term"

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        results = (
            spotify.current_user_top_tracks(
                limit=20,
                time_range=time_range
            )
        )

        tracks = []

        for item in results.get(
            "items",
            []
        ):

            artists = item.get(
                "artists",
                []
            )

            primary_artist = (
                artists[0]
                if artists
                else {}
            )

            album = item.get(
                "album",
                {}
            )

            album_images = album.get(
                "images",
                []
            )

            tracks.append({

                "name": item.get(
                    "name",
                    ""
                ),

                "artist": (
                    primary_artist.get(
                        "name",
                        ""
                    )
                ),

                "artist_id": (
                    primary_artist.get(
                        "id"
                    )
                ),

                "artist_image_url": (
                    spotify_artist_image_url(
                        spotify,
                        primary_artist.get(
                            "id"
                        )
                    )
                ),

                "album": album.get(
                    "name",
                    ""
                ),

                "track_id": item.get(
                    "id"
                ),

                "duration_ms": item.get(
                    "duration_ms",
                    0
                ),

                "spotify_url": (
                    item.get(
                        "external_urls",
                        {}
                    ).get(
                        "spotify"
                    )
                ),

                "image_url": (
                    album_images[0]["url"]
                    if album_images
                    else None
                ),
            })

        return {
            "total": len(tracks),
            "tracks": tracks,
            "source": "spotify"
        }

    except Exception as error:

        print(
            "TOP TRACKS ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# TOP ARTISTS
# --------------------------------------------------

@app.get("/top-artists")
def top_artists(
    request: Request,
    time_range: str = "medium_term"
):

    if time_range not in {
        "short_term",
        "medium_term",
        "long_term"
    }:

        time_range = "medium_term"

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        results = (
            spotify.current_user_top_artists(
                limit=20,
                time_range=time_range
            )
        )

        artists = []

        for item in results.get(
            "items",
            []
        ):

            images = item.get(
                "images",
                []
            )

            artists.append({

                "name": item.get(
                    "name",
                    ""
                ),

                "artist_id": item.get(
                    "id"
                ),

                "spotify_url": (
                    item.get(
                        "external_urls",
                        {}
                    ).get(
                        "spotify"
                    )
                ),

                "image_url": (
                    images[0]["url"]
                    if images
                    else None
                ),
            })

        return {

            "total": len(artists),

            "artists": artists,

            "source": "spotify"
        }

    except Exception as error:

        print(
            "TOP ARTISTS ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# RECENTLY PLAYED
# --------------------------------------------------

@app.get("/recently-played")
def recently_played(
    request: Request
):

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        results = (
            spotify.current_user_recently_played(
                limit=20
            )
        )

        tracks = []

        for item in results.get(
            "items",
            []
        ):

            track = item.get(
                "track"
            )

            if not track:
                continue

            artists = track.get(
                "artists",
                []
            )

            album = track.get(
                "album",
                {}
            )

            album_images = album.get(
                "images",
                []
            )

            tracks.append({

                "name": track.get(
                    "name",
                    ""
                ),

                "artist": ", ".join(
                    artist.get(
                        "name",
                        ""
                    )
                    for artist in artists
                ),

                "album": album.get(
                    "name",
                    ""
                ),

                "played_at": item.get(
                    "played_at"
                ),

                "duration_ms": track.get(
                    "duration_ms",
                    0
                ),

                "spotify_url": (
                    track.get(
                        "external_urls",
                        {}
                    ).get(
                        "spotify"
                    )
                ),

                "image_url": (
                    album_images[0]["url"]
                    if album_images
                    else None
                ),
            })

        return {

            "total": len(tracks),

            "recently_played": tracks,

            "source": "spotify"
        }

    except Exception as error:

        print(
            "RECENTLY PLAYED ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# PLAYLISTS
# --------------------------------------------------

@app.get("/playlists")
def playlists(
    request: Request
):

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        playlists = []

        offset = 0

        while True:

            results = (
                spotify.current_user_playlists(
                    limit=50,
                    offset=offset
                )
            )

            items = results.get(
                "items",
                []
            )

            if not items:
                break

            for item in items:

                images = item.get(
                    "images",
                    []
                )

                playlist_items = item.get(
                    "items",
                    {}
                )

                playlists.append({

                    "id": item.get(
                        "id"
                    ),

                    "name": item.get(
                        "name"
                    ),

                    "description": item.get(
                        "description"
                    ),

                    "tracks_total": (
                        playlist_items.get(
                            "total",
                            0
                        )
                    ),

                    "spotify_url": (
                        item.get(
                            "external_urls",
                            {}
                        ).get(
                            "spotify"
                        )
                    ),

                    "image_url": (
                        images[0]["url"]
                        if images
                        else None
                    ),
                })

            if not results.get(
                "next"
            ):

                break

            offset += len(items)

        return {

            "total": len(playlists),

            "playlists": playlists
        }

    except Exception as error:

        print(
            "PLAYLISTS ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# PLAYLIST TRACKS
# --------------------------------------------------

@app.get("/playlist-tracks")
def playlist_tracks(
    request: Request,
    playlist_id: str
):

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        tracks = []

        offset = 0

        while True:

            results = spotify._get(
                f"playlists/{playlist_id}/items",
                limit=50,
                offset=offset
            )

            items = results.get(
                "items",
                []
            )

            if not items:
                break

            for item in items:

                track = item.get(
                    "item"
                )

                if not track:
                    continue

                if track.get(
                    "type"
                ) != "track":

                    continue

                artists = track.get(
                    "artists",
                    []
                )

                album = track.get(
                    "album",
                    {}
                )

                album_images = album.get(
                    "images",
                    []
                )

                tracks.append({

                    "name": track.get(
                        "name"
                    ),

                    "artist": (
                        artists[0].get(
                            "name",
                            ""
                        )
                        if artists
                        else ""
                    ),

                    "album": album.get(
                        "name"
                    ),

                    "duration_ms": track.get(
                        "duration_ms"
                    ),

                    "spotify_url": (
                        track.get(
                            "external_urls",
                            {}
                        ).get(
                            "spotify"
                        )
                    ),

                    "image_url": (
                        album_images[0]["url"]
                        if album_images
                        else None
                    ),
                })

            if not results.get(
                "next"
            ):

                break

            offset += len(items)

        return {

            "total": len(tracks),

            "tracks": tracks
        }

    except Exception as error:

        print(
            "PLAYLIST TRACKS ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.get("/analytics")
def analytics(
    request: Request,
    time_range: str = "medium_term"
):

    if time_range not in {
        "short_term",
        "medium_term",
        "long_term"
    }:

        time_range = "medium_term"

    try:

        spotify = get_authenticated_spotify(
            request
        )

        if not spotify:

            return {
                "error": "Not authenticated"
            }

        # --------------------------------------------------
        # GET THE USER'S LIVE TOP TRACKS
        # --------------------------------------------------

        results = (
            spotify.current_user_top_tracks(
                limit=50,
                time_range=time_range
            )
        )

        items = results.get(
            "items",
            []
        )

        if not items:

            return {
                "time_range": time_range,

                "summary": {
                    "tracks": 0,
                    "unique_albums": 0,
                    "average_duration": 0,
                    "explicit_percent": 0,
                    "collaboration_percent": 0,
                },

                "release_years": [],
                "release_decades": [],
                "durations": [],
                "album_types": [],
                "albums": [],
                "artist_pyramid": [],
                "recent_count": 0,
            }

        rows = []

        for item in items:

            album = item.get(
                "album",
                {}
            )

            release_date = album.get(
                "release_date"
            )

            release_year = None

            if release_date:

                try:

                    release_year = int(
                        str(
                            release_date
                        )[:4]
                    )

                except Exception:

                    release_year = None

            artists = item.get(
                "artists",
                []
            )

            artist_names = [
                artist.get(
                    "name",
                    ""
                )
                for artist in artists
            ]

            rows.append({

                "Track Name": item.get(
                    "name",
                    ""
                ),

                "Album": album.get(
                    "name",
                    ""
                ),

                "Duration (Minutes)": (
                    float(
                        item.get(
                            "duration_ms",
                            0
                        )
                    ) / 60000
                ),

                "Explicit": bool(
                    item.get(
                        "explicit",
                        False
                    )
                ),

                "Release Year": release_year,

                "Release Decade": (
                    (release_year // 10) * 10
                    if release_year
                    else None
                ),

                "Album Type": album.get(
                    "album_type",
                    "album"
                ),

                "Artists": ", ".join(
                    artist_names
                ),
            })

        tracks = pd.DataFrame(
            rows
        )

        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------

        total_tracks = len(
            tracks
        )

        explicit_count = int(
            tracks["Explicit"].sum()
        )

        duration = tracks[
            "Duration (Minutes)"
        ].dropna()

        # --------------------------------------------------
        # COUNTS HELPER
        # --------------------------------------------------

        def counts(
            column,
            limit=8
        ):

            if (
                tracks.empty
                or column not in tracks
            ):

                return []

            values = (
                tracks[column]
                .dropna()
            )

            values = values[
                values.astype(str)
                .str.strip()
                .str.lower()
                != "unknown"
            ]

            result = []

            for label, value in (
                values
                .value_counts()
                .head(limit)
                .items()
            ):

                if isinstance(
                    label,
                    (int, float)
                ) and pd.notna(label):

                    label = str(
                        int(label)
                    )

                else:

                    label = str(
                        label
                    )

                result.append({

                    "label": label,

                    "value": int(
                        value
                    )
                })

            return result

        # --------------------------------------------------
        # ARTIST COUNTS
        # --------------------------------------------------

        artist_counts = {}

        for artists in tracks[
            "Artists"
        ].fillna(""):

            for artist in str(
                artists
            ).split(","):

                artist = artist.strip()

                if artist:

                    artist_counts[
                        artist
                    ] = (
                        artist_counts.get(
                            artist,
                            0
                        ) + 1
                    )

        pyramid = [

            {
                "name": name,
                "value": value
            }

            for name, value in sorted(
                artist_counts.items(),
                key=lambda item: (
                    -item[1],
                    item[0]
                )
            )[:7]
        ]

        # --------------------------------------------------
        # RELEASE YEARS
        # --------------------------------------------------

        release_years = counts(
            "Release Year",
            20
        )

        release_years.sort(
            key=lambda item:
            int(item["label"])
            if item["label"].isdigit()
            else 9999
        )

        # --------------------------------------------------
        # RELEASE DECADES
        # --------------------------------------------------

        release_decades = counts(
            "Release Decade",
            8
        )

        release_decades.sort(
            key=lambda item:
            int(item["label"])
            if item["label"].isdigit()
            else 9999
        )

        # --------------------------------------------------
        # RECENTLY PLAYED COUNT
        # --------------------------------------------------

        recent_count = 0

        try:

            recent_results = (
                spotify.current_user_recently_played(
                    limit=50
                )
            )

            recent_count = len(
                recent_results.get(
                    "items",
                    []
                )
            )

        except Exception as recent_error:

            print(
                "ANALYTICS RECENT ERROR:",
                repr(recent_error)
            )

        # --------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------

        return {

            "time_range": time_range,

            "summary": {

                "tracks": total_tracks,

                "unique_albums": int(
                    tracks[
                        "Album"
                    ].nunique()
                ),

                "average_duration": (
                    round(
                        float(
                            duration.mean()
                        ),
                        2
                    )
                    if not duration.empty
                    else 0
                ),

                "explicit_percent": (
                    round(
                        (
                            explicit_count
                            / total_tracks
                        ) * 100
                    )
                    if total_tracks
                    else 0
                ),

                "collaboration_percent": (
                    round(
                        sum(
                            len(
                                str(
                                    artists
                                ).split(",")
                            ) > 1
                            for artists in tracks[
                                "Artists"
                            ].fillna("")
                        )
                        / total_tracks
                        * 100
                    )
                    if total_tracks
                    else 0
                ),
            },

            "release_years": (
                release_years
            ),

            "release_decades": (
                release_decades
            ),

            "durations": counts(
                "Duration Bucket",
                8
            ),

            "album_types": counts(
                "Album Type",
                5
            ),

            "albums": counts(
                "Album",
                8
            ),

            "artist_pyramid": pyramid,

            "recent_count": recent_count,
        }

    except Exception as error:

        print(
            "ANALYTICS ERROR:",
            repr(error)
        )

        return {
            "error": str(error)
        }