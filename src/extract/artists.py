import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)


def save_csv(df, filename):
    path = RAW_FOLDER / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}")


def extract_top_artists(sp):

    print("Extracting Top Artists...")

    results = sp.current_user_top_artists(limit=50)

    rows = []

    for artist in results["items"]:

        image = ""

        if artist.get("images"):
            image = artist["images"][0].get("url", "")

        rows.append({
            "Artist ID": artist["id"],
            "Artist Name": artist["name"],
            "Genres": ", ".join(artist.get("genres", [])),
            "Followers": artist.get("followers", {}).get("total", 0),
            "Popularity": artist.get("popularity", 0),
            "Spotify URL": artist.get("external_urls", {}).get("spotify", ""),
            "Image": image
        })

    df = pd.DataFrame(rows)

    save_csv(df, "top_artists.csv")

    print("✓ Top Artists extracted")

    return df