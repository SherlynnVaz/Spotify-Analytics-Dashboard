import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)


def save_csv(df, filename):
    path = RAW_FOLDER / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}")


def extract_top_tracks(sp):

    print("Extracting Top Tracks...")

    results = sp.current_user_top_tracks(
        limit=50,
        time_range="medium_term"
    )

    rows = []

    for track in results["items"]:

        rows.append({

            "Track ID": track["id"],

            "Track Name": track["name"],

            "Album ID": track["album"].get("id", ""),

            "Album": track["album"]["name"],

            "Artist IDs": ",".join(
                artist["id"]
                for artist in track["artists"]
            ),

            "Artists": ", ".join(
                artist["name"]
                for artist in track["artists"]
            ),

            "Duration_ms": track["duration_ms"],

            "Explicit": track["explicit"],

            "Track Number": track["track_number"],

            "Disc Number": track["disc_number"],

            "Preview URL": track.get("preview_url", ""),

            "Spotify URL": track["external_urls"].get("spotify", ""),

        })

    df = pd.DataFrame(rows)

    save_csv(df, "top_tracks.csv")

    return df