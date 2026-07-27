import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

def save_csv(df, filename):
    path = RAW_FOLDER / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}")

def extract_recently_played(sp):
    print("Extracting Recently Played...")
    results = sp.current_user_recently_played(limit=50)

    rows = []

    for item in results["items"]:
        track = item["track"]

        rows.append({
            "Played At": item.get("played_at", ""),
            "Track ID": track["id"],
            "Track Name": track["name"],
            "Artist": ", ".join(
                artist["name"] for artist in track["artists"]
            ),
            "Album": track["album"]["name"],
            "Duration_ms": track["duration_ms"],
            "Popularity": track.get("popularity", 0),
            "Explicit": track["explicit"],
            "Preview URL": track.get("preview_url", ""),
            "Spotify URL": track["external_urls"].get("spotify", "")
        })

    df = pd.DataFrame(rows)

    save_csv(df, "recently_played.csv")

    print("✓ Recently Played extracted")

    return df