from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from urllib.parse import urlencode
import pandas as pd
import requests

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
spotify_user = None
PROJECT_ROOT = Path(__file__).resolve().parent.parent
artwork_cache = {}


def get_authenticated_spotify():
    if not spotify_token:
        return None

    return spotipy.Spotify(
        auth=spotify_token["access_token"],
        retries=0
    )


def spotify_artwork_url(item_type, item_id):
    cache_key = f"{item_type}:{item_id}"

    if cache_key in artwork_cache:
        return artwork_cache[cache_key]

    try:
        response = requests.get(
            "https://open.spotify.com/oembed",
            params={
                "url": f"https://open.spotify.com/{item_type}/{item_id}"
            },
            timeout=4,
        )

        artwork_url = response.json().get("thumbnail_url")
        artwork_cache[cache_key] = artwork_url

        return artwork_url

    except Exception as error:
        print("ARTWORK LOOKUP ERROR:", repr(error))
        return None


@app.get("/artwork/{item_type}/{item_id}")
def artwork(item_type: str, item_id: str):
    if item_type not in {"track", "artist"}:
        return {"error": "Unsupported artwork type"}

    artwork_url = spotify_artwork_url(item_type, item_id)

    if not artwork_url:
        return {"error": "Artwork unavailable"}

    return RedirectResponse(url=artwork_url)


def _analytics_rows(time_range):
    range_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"top_tracks_{time_range}_clean.csv"
    )

    metadata_file = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "top_tracks.csv"
    )

    tracks = (
        pd.read_csv(range_file)
        if range_file.exists()
        else pd.DataFrame()
    )

    metadata = (
        pd.read_csv(metadata_file)
        if metadata_file.exists()
        else pd.DataFrame()
    )

    if (
        not tracks.empty
        and not metadata.empty
        and "Track ID" in tracks
        and "Track ID" in metadata
    ):
        metadata_columns = [
            column
            for column in [
                "Track ID",
                "Release Date",
                "Release Year",
                "Release Decade",
                "Album Type",
                "Explicit",
                "Popularity",
            ]
            if column in metadata.columns
        ]

        tracks = tracks.merge(
            metadata[metadata_columns],
            on="Track ID",
            how="left"
        )

    if "Explicit" not in tracks:
        tracks["Explicit"] = False

    if "Album Type" not in tracks:
        tracks["Album Type"] = "Album"

    if "Release Year" not in tracks:
        tracks["Release Year"] = pd.to_datetime(
            tracks.get("Release Date"),
            errors="coerce"
        ).dt.year

    tracks["Release Decade"] = (
        pd.to_numeric(
            tracks["Release Year"],
            errors="coerce"
        )
        // 10
        * 10
    )

    tracks["Explicit"] = tracks["Explicit"].fillna(False).apply(
        lambda value:
            value
            if isinstance(value, bool)
            else str(value).lower() == "true"
    )

    tracks["Album Type"] = (
        tracks["Album Type"]
        .fillna("Album")
        .astype(str)
        .str.strip()
        .str.title()
    )

    tracks["Duration (Minutes)"] = pd.to_numeric(
        tracks.get("Duration (Minutes)"),
        errors="coerce"
    )

    tracks = (
        tracks.dropna(subset=["Track Name"])
        if not tracks.empty
        else tracks
    )

    return tracks


@app.get("/analytics")
def analytics(time_range: str = "medium_term"):
    if time_range not in {
        "short_term",
        "medium_term",
        "long_term"
    }:
        time_range = "medium_term"

    try:
        tracks = _analytics_rows(time_range)

        recent_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / "recently_played_clean.csv"
        )

        recent = (
            pd.read_csv(recent_file)
            if recent_file.exists()
            else pd.DataFrame()
        )

        def counts(column, limit=8):
            if tracks.empty or column not in tracks:
                return []

            values = tracks[column].dropna()

            values = values[
                values.astype(str).str.strip().str.lower() != "unknown"
            ]

            return [
                {
                    "label": (
                        str(int(label))
                        if isinstance(label, (int, float))
                        and pd.notna(label)
                        else str(label)
                    ),
                    "value": int(value),
                }
                for label, value
                in values.value_counts().head(limit).items()
            ]

        artist_counts = {}

        for artists in tracks.get(
            "Artists",
            pd.Series(dtype=str)
        ).fillna(""):

            for artist in str(artists).split(","):
                artist = artist.strip()

                if artist:
                    artist_counts[artist] = (
                        artist_counts.get(artist, 0) + 1
                    )

        pyramid = [
            {
                "name": name,
                "value": value
            }
            for name, value
            in sorted(
                artist_counts.items(),
                key=lambda item: (-item[1], item[0])
            )[:7]
        ]

        duration = (
            tracks["Duration (Minutes)"].dropna()
            if not tracks.empty
            else pd.Series(dtype=float)
        )

        explicit_count = (
            int(tracks["Explicit"].sum())
            if not tracks.empty
            else 0
        )

        total_tracks = len(tracks)

        release_years = counts("Release Year", 20)

        release_years.sort(
            key=lambda item:
                int(item["label"])
                if item["label"].isdigit()
                else 9999
        )

        release_decades = counts("Release Decade", 8)

        release_decades.sort(
            key=lambda item:
                int(item["label"])
                if item["label"].isdigit()
                else 9999
        )

        return {
            "time_range": time_range,

            "summary": {
                "tracks": total_tracks,

                "unique_albums": (
                    int(tracks["Album"].nunique())
                    if "Album" in tracks
                    else 0
                ),

                "average_duration": (
                    round(float(duration.mean()), 2)
                    if not duration.empty
                    else 0
                ),

                "explicit_percent": (
                    round(
                        (explicit_count / total_tracks) * 100
                    )
                    if total_tracks
                    else 0
                ),

                "collaboration_percent": (
                    round(
                        sum(
                            value > 1
                            for value in tracks.get(
                                "Artists",
                                pd.Series(dtype=str)
                            )
                            .fillna("")
                            .str.count(",") + 1
                        )
                        / total_tracks
                        * 100
                    )
                    if total_tracks
                    else 0
                ),
            },

            "release_years": release_years,

            "release_decades": release_decades,

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

            "recent_count": len(recent),
        }

    except Exception as error:
        print("ANALYTICS ERROR:", repr(error))
        return {"error": str(error)}


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

    authorization_url = (
        "https://accounts.spotify.com/authorize?"
        + urlencode({
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),

            "response_type": "code",

            "redirect_uri": os.getenv(
                "SPOTIFY_REDIRECT_URI"
            ),

            "scope": (
                "user-top-read "
                "user-read-recently-played "
                "user-read-email "
                "playlist-read-private"
            ),

            "show_dialog": "false",
        })
    )

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
    global spotify_token, spotify_user

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
            auth=token_info["access_token"],
            retries=0
        )

        try:
            user = spotify.current_user()

            spotify_user = {
                "id": user.get("id"),
                "display_name": user.get("display_name"),
                "email": user.get("email"),
                "image_url": (
                    user["images"][0]["url"]
                    if user.get("images")
                    else None
                )
            }

            print(
                f"Spotify login successful: "
                f"{spotify_user.get('display_name')}"
            )

        except Exception as profile_error:
            print(
                "SPOTIFY PROFILE LOOKUP ERROR:",
                repr(profile_error)
            )

            spotify_user = {
                "id": None,
                "display_name": "Spotify listener",
                "email": None,
                "image_url": None,
            }

            print(
                "Spotify login successful: "
                "Spotify listener"
            )

        return RedirectResponse(
            url="http://localhost:5173/"
        )

    except Exception as e:
        print(
            "SPOTIFY AUTH ERROR:",
            repr(e)
        )

        return {
            "message": "Spotify authorization failed",
            "error": str(e)
        }
# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------

@app.get("/me")
def current_user():

    if spotify_user:
        return {
            "authenticated": True,
            "user": spotify_user,
        }

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

                "display_name": user.get(
                    "display_name"
                ),

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


@app.post("/logout")
def logout():

    global spotify_token, spotify_user

    spotify_token = None
    spotify_user = None

    return {
        "logged_out": True
    }


# --------------------------------------------------
# TOP TRACKS
# --------------------------------------------------

@app.get("/top-tracks")
def top_tracks(
    time_range: str = "medium_term"
):

    try:

        processed_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / f"top_tracks_{time_range}_clean.csv"
        )

        if processed_file.exists():

            processed_tracks = (
                pd.read_csv(processed_file)
                .fillna("")
            )

            raw_tracks_file = (
                PROJECT_ROOT
                / "data"
                / "raw"
                / "top_tracks.csv"
            )

            raw_tracks = (
                pd.read_csv(raw_tracks_file)
                .fillna("")
                if raw_tracks_file.exists()
                else pd.DataFrame()
            )

            raw_artist_ids = {
                row.get("Track ID"):
                    str(
                        row.get(
                            "Artist IDs",
                            ""
                        )
                    )
                    .split(",")[0]
                    .strip()

                for _, row in raw_tracks.iterrows()
            }

            tracks = [

                {
                    "name": row.get(
                        "Track Name",
                        ""
                    ),

                    "artist": row.get(
                        "Artists",
                        ""
                    ),

                    "album": row.get(
                        "Album",
                        ""
                    ),

                    "track_id": row.get(
                        "Track ID",
                        ""
                    ),

                    "artist_image_url": (
                        f"http://127.0.0.1:8000/"
                        f"artwork/artist/"
                        f"{raw_artist_ids.get(row.get('Track ID'), '')}"
                        if raw_artist_ids.get(
                            row.get("Track ID")
                        )
                        else None
                    ),

                    "duration_ms": round(
                        float(
                            row.get(
                                "Duration (Minutes)",
                                0
                            )
                        ) * 60000
                    ),

                    "spotify_url": "",

                    "image_url": (
                        f"http://127.0.0.1:8000/"
                        f"artwork/track/"
                        f"{row.get('Track ID', '')}"
                    ),
                }

                for _, row
                in processed_tracks.iterrows()
            ]

            return {
                "total": len(tracks),
                "tracks": tracks
            }

        spotify = get_authenticated_spotify()

        if not spotify:
            return {
                "error": "Not authenticated"
            }

        results = spotify.current_user_top_tracks(
            limit=20,
            time_range=time_range
        )

        tracks = []

        for item in results["items"]:

            primary_artist = item["artists"][0]

            artist_image_url = None

            try:

                artist_details = spotify.artist(
                    primary_artist["id"]
                )

                artist_image_url = (
                    artist_details["images"][0]["url"]
                    if artist_details.get("images")
                    else None
                )

            except Exception as artist_error:

                print(
                    "ARTIST IMAGE ERROR:",
                    repr(artist_error)
                )

            tracks.append({

                "name": item["name"],

                "artist": item["artists"][0]["name"],

                "artist_image_url": artist_image_url,

                "album": item["album"]["name"],

                "duration_ms": item["duration_ms"],

                "spotify_url": (
                    item["external_urls"]["spotify"]
                ),

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

        print(
            "TOP TRACKS ERROR:",
            repr(e)
        )

        return {
            "error": str(e)
        }


# --------------------------------------------------
# TOP ARTISTS
# --------------------------------------------------

@app.get("/top-artists")
def top_artists(
    time_range: str = "medium_term"
):

    try:

        processed_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / f"top_artists_{time_range}_clean.csv"
        )

        spotify = get_authenticated_spotify()

        if spotify:

            try:

                results = (
                    spotify.current_user_top_artists(
                        limit=20,
                        time_range=time_range
                    )
                )

                artists = [

                    {
                        "name": item["name"],

                        "artist_id": item.get(
                            "id"
                        ),

                        "spotify_url": (
                            item["external_urls"]["spotify"]
                        ),

                        "image_url": (
                            item["images"][0]["url"]
                            if item.get("images")
                            else None
                        )
                    }

                    for item in results["items"]
                ]

                return {
                    "total": len(artists),
                    "artists": artists,
                    "source": "spotify"
                }

            except Exception as spotify_error:

                print(
                    "TOP ARTISTS SPOTIFY ERROR:",
                    repr(spotify_error)
                )

        if processed_file.exists():

            processed_artists = (
                pd.read_csv(processed_file)
                .fillna("")
            )

            artists = [

                {
                    "name": row.get(
                        "Artist Name",
                        ""
                    ),

                    "artist_id": row.get(
                        "Artist ID",
                        ""
                    ),

                    "spotify_url": "",

                    "image_url": (
                        f"http://127.0.0.1:8000/"
                        f"artwork/artist/"
                        f"{row.get('Artist ID', '')}"
                    )
                }

                for _, row
                in processed_artists.iterrows()
            ]

            return {
                "total": len(artists),
                "artists": artists,
                "source": "processed_fallback"
            }

        return {
            "error": "Not authenticated"
        }

    except Exception as e:

        print(
            "TOP ARTISTS ERROR:",
            repr(e)
        )

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

        if spotify:

            try:

                results = (
                    spotify.current_user_recently_played(
                        limit=20
                    )
                )

                tracks = []

                for item in results["items"]:

                    track = item["track"]

                    tracks.append({

                        "name": track["name"],

                        "artist": ", ".join(
                            artist["name"]
                            for artist
                            in track.get(
                                "artists",
                                []
                            )
                        ),

                        "album": track["album"]["name"],

                        "played_at": item["played_at"],

                        "duration_ms": track[
                            "duration_ms"
                        ],

                        "spotify_url": (
                            track[
                                "external_urls"
                            ]["spotify"]
                        ),

                        "image_url": (
                            track["album"]["images"][0]["url"]
                            if track["album"].get("images")
                            else None
                        )
                    })

                return {
                    "total": len(tracks),
                    "recently_played": tracks,
                    "source": "spotify"
                }

            except Exception as spotify_error:

                print(
                    "RECENTLY PLAYED SPOTIFY ERROR:",
                    repr(spotify_error)
                )

        recent_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / "recently_played_clean.csv"
        )

        if recent_file.exists():

            recent = (
                pd.read_csv(recent_file)
                .fillna("")
                .head(20)
            )

            tracks = [

                {
                    "name": row.get(
                        "Track Name",
                        ""
                    ),

                    "artist": row.get(
                        "Artist",
                        ""
                    ),

                    "album": row.get(
                        "Album",
                        ""
                    ),

                    "played_at": (
                        f"{row.get('Played Date', '')}"
                        f"T{row.get('Played Time', '')}+05:30"
                    ),

                    "duration_ms": round(
                        float(
                            row.get(
                                "Duration (Minutes)",
                                0
                            )
                        ) * 60000
                    ),

                    "spotify_url": row.get(
                        "Spotify URL",
                        ""
                    ),

                    "image_url": (
                        f"http://127.0.0.1:8000/"
                        f"artwork/track/"
                        f"{row.get('Track ID', '')}"
                    )
                }

                for _, row
                in recent.iterrows()
            ]

            return {
                "total": len(tracks),
                "recently_played": tracks,
                "source": "processed_fallback"
            }

        return {
            "error": "Not authenticated"
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

                "description": item.get(
                    "description"
                ),

                "tracks_total": item["items"]["total"],

                "spotify_url": (
                    item["external_urls"]["spotify"]
                ),

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
def playlist_tracks(
    playlist_id: str
):

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

        for item in results.get(
            "items",
            []
        ):

            track = item.get("item")

            if not track:
                continue

            if track.get("type") != "track":
                continue

            tracks.append({

                "name": track.get(
                    "name"
                ),

                "artist": track[
                    "artists"
                ][0]["name"],

                "album": track[
                    "album"
                ]["name"],

                "duration_ms": track.get(
                    "duration_ms"
                ),

                "spotify_url": track[
                    "external_urls"
                ]["spotify"],

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

        print(
            "PLAYLIST ERROR:",
            repr(e)
        )

        return {
            "error": str(e)
        }