import pandas as pd
from pathlib import Path
from spotipy.exceptions import SpotifyException

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)


def save_csv(df, filename):
    path = RAW_FOLDER / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}")


def extract_playlists(sp):

    print("Extracting Playlists...")

    playlists = sp.current_user_playlists(limit=50)

    playlist_rows = []
    playlist_track_rows = []

    for playlist in playlists["items"]:

        playlist_rows.append({

            "Playlist ID": playlist.get("id", ""),
            "Playlist Name": playlist.get("name", ""),
            "Owner": playlist.get("owner", {}).get("display_name", ""),
            "Public": playlist.get("public", False),
            "Collaborative": playlist.get("collaborative", False),
            "Tracks": playlist.get("tracks", {}).get("total", 0),

        })

        try:
            results = sp.playlist_tracks(playlist["id"])
        except SpotifyException as error:
            if error.http_status == 403:
                print(f"Skipping playlist {playlist.get('name', playlist['id'])}: access forbidden")
                continue
            raise

        for item in results["items"]:

            track = item.get("track")

            if track:

                playlist_track_rows.append({

                    "Playlist ID": playlist["id"],
                    "Track ID": track["id"]

                })

    playlists_df = pd.DataFrame(playlist_rows)
    playlist_tracks_df = pd.DataFrame(playlist_track_rows)

    save_csv(playlists_df, "playlists.csv")
    save_csv(playlist_tracks_df, "playlist_tracks.csv")

    return playlists_df, playlist_tracks_df