import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)


def fix_encoding(text):
    if pd.isna(text):
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def transform_tracks():
    print("Transforming Top Tracks...")

    df = pd.read_csv(RAW_FOLDER / "top_tracks.csv")

    # Remove duplicates and invalid rows
    df = df.drop_duplicates()
    df = df.dropna(subset=["Track Name"])

    # Fix encoding
    df["Track Name"] = df["Track Name"].apply(fix_encoding)
    df["Album"] = df["Album"].apply(fix_encoding)
    df["Artists"] = df["Artists"].apply(fix_encoding)

    # Convert duration
    df["Duration (Minutes)"] = (df["Duration_ms"] / 60000).round(2)

    # Release Date
    df["Release Date"] = pd.to_datetime(
        df["Release Date"],
        errors="coerce"
    )

    df["Release Year"] = df["Release Date"].dt.year

    df["Release Decade"] = (
        df["Release Year"] // 10
    ) * 10

    # Duration Buckets
    df["Duration Bucket"] = pd.cut(
        df["Duration (Minutes)"],
        bins=[0, 2, 3, 4, 5, 100],
        labels=[
            "<2 min",
            "2-3 min",
            "3-4 min",
            "4-5 min",
            "5+ min"
        ]
    )

    # Remove unnecessary columns
    df.drop(
        columns=[
            "Duration_ms",
            "URI",
            "Is Local",
            "Preview URL",
            "Disc Number",
            "Track Number"
        ],
        errors="ignore",
        inplace=True
    )

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
    df["Artist Name"] = df["Artist Name"].apply(fix_encoding)

    # Remove unusable columns
    df.drop(
        columns=[
            "Followers",
            "Genres",
            "Popularity"
        ],
        errors="ignore",
        inplace=True
    )

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

    df = df.drop_duplicates()
    df = df.dropna(subset=["Playlist Name"])
    df["Playlist Name"] = df["Playlist Name"].apply(fix_encoding)
    df["Owner"] = df["Owner"].apply(fix_encoding)

    df["Tracks"] = (
        df["Tracks"]
        .fillna(0)
        .astype(int)
    )

    # Remove unnecessary column
    df.drop(
        columns=["Collaborative"],
        errors="ignore",
        inplace=True
    )

    df = df.sort_values(
        by="Tracks",
        ascending=False
    )

    df.reset_index(drop=True, inplace=True)

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

    df = df.drop_duplicates()
    df = df.dropna(subset=["Track Name"])

    # Fix encoding
    df["Track Name"] = df["Track Name"].apply(fix_encoding)
    df["Artist"] = df["Artist"].apply(fix_encoding)
    df["Album"] = df["Album"].apply(fix_encoding)

    # ============================================================
    # CONVERT PLAYED AT FROM UTC TO INDIA STANDARD TIME
    # ============================================================

    df["Played At"] = pd.to_datetime(
        df["Played At"],
        errors="coerce",
        utc=True
    )

    # Convert UTC → IST
    df["Played At"] = df["Played At"].dt.tz_convert("Asia/Kolkata")


    # ============================================================
    # CREATE USEFUL DATE/TIME COLUMNS
    # ============================================================

    df["Played Date"] = df["Played At"].dt.date

    df["Played Time"] = df["Played At"].dt.strftime("%H:%M:%S")

    df["Hour Played"] = df["Played At"].dt.hour

    df["Hour Label"] = (
        df["Played At"]
        .dt.strftime("%I %p")
        .str.lstrip("0")
        .str.strip()
    )

    # Convert duration
    df["Duration (Minutes)"] = (
        df["Duration_ms"] / 60000
    ).round(2)

    # Remove unnecessary columns
    df.drop(
        columns=[
            "Played At",
            "Duration_ms",
            "Popularity",
            "Preview URL",
            "Day Name",
            "Weekday Number"
        ],
        errors="ignore",
        inplace=True
    )

    df.reset_index(drop=True, inplace=True)

    df.to_csv(
        PROCESSED_FOLDER / "recently_played_clean.csv",
        index=False
    )

    print("Saved recently_played_clean.csv")
    print("✓ Recently Played transformed")

    return df

def create_track_artist_bridge():
    print("Creating Track-Artist Bridge...")

    df = pd.read_csv(PROCESSED_FOLDER / "top_tracks_clean.csv")

    bridge_rows = []

    for _, row in df.iterrows():

        track_id = row["Track ID"]

        artist_ids = str(row["Artist IDs"]).split(",")
        artist_names = str(row["Artists"]).split(",")

        artist_ids = [a.strip() for a in artist_ids]
        artist_names = [a.strip() for a in artist_names]

        for artist_id, artist_name in zip(artist_ids, artist_names):
            bridge_rows.append({
                "Track ID": track_id,
                "Artist ID": artist_id,
                "Artist Name": artist_name
            })

    bridge_df = pd.DataFrame(bridge_rows)

    bridge_df = bridge_df.drop_duplicates()

    bridge_df = bridge_df.sort_values(
        ["Track ID", "Artist Name"]
    )

    bridge_df.reset_index(drop=True, inplace=True)

    bridge_df.to_csv(
        PROCESSED_FOLDER / "bridge_track_artist.csv",
        index=False
    )

    print("Saved bridge_track_artist.csv")

    return bridge_df


if __name__ == "__main__":
    transform_tracks()
    transform_artists()
    transform_playlists()
    transform_recently_played()
    create_track_artist_bridge()