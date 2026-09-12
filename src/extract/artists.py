import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)


def extract_top_artists(sp):

    time_ranges = {
        "short_term": "4 Weeks",
        "medium_term": "6 Months",
        "long_term": "All Time"
    }

    for time_range, label in time_ranges.items():

        print(f"Extracting Top Artists — {label}...")

        results = sp.current_user_top_artists(
            limit=50,
            time_range=time_range
        )

        rows = []

        for rank, artist in enumerate(
            results["items"],
            start=1
        ):

            genres = ", ".join(
                artist.get("genres", [])
            )

            rows.append({
                "Rank": rank,
                "Artist ID": artist.get("id"),
                "Artist Name": artist.get("name"),
                "Genres": genres,
                "Followers": artist.get(
                    "followers", {}
                ).get("total"),
                "Time Range": time_range
            })

        df = pd.DataFrame(rows)

        output_file = (
            RAW_FOLDER /
            f"top_artists_{time_range}.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"Saved {output_file.name} "
            f"({len(df)} artists)"
        )

    print("✓ Top Artists extraction completed")