import os
import pandas as pd

FILES = [
    ("top_tracks_clean.csv", 15),
    ("top_artists_clean.csv", 15),
    ("top_playlists_clean.csv", 10),
    ("recently_played_clean.csv", 15),
]

processed_dir = "data/processed"
sample_dir = "data/sample"


def create_sample_data():
    os.makedirs(sample_dir, exist_ok=True)

    for filename, rows in FILES:
        df = pd.read_csv(os.path.join(processed_dir, filename))
        df.head(rows).to_csv(
            os.path.join(sample_dir, filename),
            index=False
        )

    print("Sample datasets created successfully!")


if __name__ == "__main__":
    create_sample_data()