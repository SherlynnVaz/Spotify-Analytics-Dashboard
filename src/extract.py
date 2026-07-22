import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

def save_csv(df, filename):

    path = RAW_FOLDER / filename
    df.to_csv(path, index=False)
    print(f"\nSaved {filename}")


def extract_top_tracks(sp):
    """
    Extract user's top tracks.
    """

    print("Extracting Top Tracks...")

    results = sp.current_user_top_tracks(limit=50)

    rows = []

    for track in results["items"]:

        rows.append({
            "Track ID": track["id"],
            "Track Name": track["name"],
            "Artist": ", ".join(
                artist["name"]
                for artist in track["artists"]
            ),
            "Album": track["album"]["name"],
            "Popularity": track.get("popularity"),
            "Duration (ms)": track["duration_ms"],
            "Explicit": track["explicit"],
            "Spotify URL": track["external_urls"]["spotify"]
        })

    df = pd.DataFrame(rows)

    save_csv(df, "top_tracks.csv")
