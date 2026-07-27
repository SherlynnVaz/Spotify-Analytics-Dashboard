import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

def transform_tracks():
    print("Transforming Top Tracks...")

    df = pd.read_csv(RAW_FOLDER / "top_tracks.csv")

    df = df.drop_duplicates()
    df = df.dropna(subset=["Track Name"])

    df["Duration (Minutes)"] = (
        df["Duration_ms"] / 60000
    ).round(2)

    df.drop(columns=["Duration_ms"], inplace=True)
    

    df["Release Date"] = pd.to_datetime(
        df["Release Date"],
        errors="coerce"
    )

    df["Release Year"] = df["Release Date"].dt.year

    df = df.sort_values(
        by="Popularity",
        ascending=False
    )

    df.reset_index(drop=True, inplace=True)

    df.to_csv(
        PROCESSED_FOLDER / "top_tracks_clean.csv",
        index=False
    )

    print("Saved top_tracks_clean.csv")

    print("✓ Top Tracks transformed")

    return df

def transform_artists():

    print("Transforming Top Artists...")

    df = pd.read_csv(RAW_FOLDER / "top_artists.csv")
    df = df.drop_duplicates()
    df = df.dropna(subset=["Artist Name"])
    df = df.sort_values(
    by="Popularity",
    ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(
    PROCESSED_FOLDER / "top_artists_clean.csv",
    index=False
    )

    print("Saved top_artists_clean.csv")

    print("✓ Top Artists transformed")

    return df

def transform_playlists():

    print("Transforming Playlists...")

    df = pd.read_csv(RAW_FOLDER / "playlists.csv")

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove playlists without a name
    df = df.dropna(subset=["Playlist Name"])

    # Convert Tracks to integer
    df["Tracks"] = df["Tracks"].fillna(0).astype(int)

    # Sort by number of tracks
    df = df.sort_values(
        by="Tracks",
        ascending=False
    )

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Save cleaned file
    df.to_csv(
        PROCESSED_FOLDER / "top_playlists_clean.csv",
        index=False
    )

    print("Saved top_playlists_clean.csv")

    print("✓ Playlists transformed")

    return df

def transform_recently_played():

    print("Transforming Recently Played...")

    df = pd.read_csv(RAW_FOLDER / "recently_played.csv")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows without a track name
    df = df.dropna(subset=["Track Name"])

    # Convert duration to minutes
    df["Duration (Minutes)"] = (
        df["Duration_ms"] / 60000
    ).round(2)

    # Convert Played At to datetime
    df["Played At"] = pd.to_datetime(
        df["Played At"],
        errors="coerce"
    )

    # Sort newest first
    df = df.sort_values(
        by="Played At",
        ascending=False
    )

    df.reset_index(drop=True, inplace=True)

    df.to_csv(
        PROCESSED_FOLDER / "recently_played_clean.csv",
        index=False
    )

    print("Saved recently_played_clean.csv")

    print("✓ Recently Played transformed")

    return df

if __name__ == "__main__":
    transform_tracks()
    transform_artists()
    transform_playlists()
    transform_recently_played()
