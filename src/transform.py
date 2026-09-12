import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

PROCESSED_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPER — FIX ENCODING
# ============================================================

def fix_encoding(text):

    if pd.isna(text):
        return text

    try:
        return text.encode("latin1").decode("utf-8")

    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


# ============================================================
# TOP TRACKS
# ============================================================

def transform_tracks():

    print("Transforming Top Tracks...")

    time_ranges = {
        "short_term": "4 Weeks",
        "medium_term": "6 Months",
        "long_term": "All Time"
    }

    transformed_dfs = {}

    for time_range, label in time_ranges.items():

        print(f"\nTransforming Top Tracks — {time_range}...")

        input_file = (
            RAW_FOLDER /
            f"top_tracks_{time_range}.csv"
        )

        # Check whether file exists
        if not input_file.exists():

            print(
                f"Skipping {time_range}: "
                f"{input_file.name} not found"
            )

            continue

        df = pd.read_csv(input_file)

        # --------------------------------------------------------
        # Remove duplicates and invalid rows
        # --------------------------------------------------------

        df = df.drop_duplicates()

        df = df.dropna(
            subset=["Track Name"]
        )

        # --------------------------------------------------------
        # Fix encoding
        # --------------------------------------------------------

        for column in [
            "Track Name",
            "Album",
            "Artists"
        ]:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .apply(fix_encoding)
                )

        # --------------------------------------------------------
        # Duration
        # --------------------------------------------------------

        if "Duration (ms)" in df.columns:

            df["Duration (Minutes)"] = (
                df["Duration (ms)"] / 60000
            ).round(2)

        elif "Duration_ms" in df.columns:

            df["Duration (Minutes)"] = (
                df["Duration_ms"] / 60000
            ).round(2)

        # --------------------------------------------------------
        # Release Date
        # --------------------------------------------------------

        if "Release Date" in df.columns:

            df["Release Date"] = pd.to_datetime(
                df["Release Date"],
                errors="coerce"
            )

            df["Release Year"] = (
                df["Release Date"].dt.year
            )

            df["Release Decade"] = (
                (df["Release Year"] // 10) * 10
            )

        # --------------------------------------------------------
        # Duration Buckets
        # --------------------------------------------------------

        if "Duration (Minutes)" in df.columns:

            df["Duration Bucket"] = pd.cut(
                df["Duration (Minutes)"],
                bins=[0, 2, 3, 4, 5, 100],
                labels=[
                    "<2 min",
                    "2-3 min",
                    "3-4 min",
                    "4-5 min",
                    "5+ min"
                ],
                include_lowest=True
            )

        # --------------------------------------------------------
        # Add Time Range
        # --------------------------------------------------------

        df["Time Range"] = label

        # --------------------------------------------------------
        # Remove unnecessary columns
        # --------------------------------------------------------

        df.drop(
            columns=[
                "Duration_ms",
                "Duration (ms)",
                "URI",
                "Is Local",
                "Preview URL",
                "Disc Number",
                "Track Number"
            ],
            errors="ignore",
            inplace=True
        )

        # --------------------------------------------------------
        # Sort
        # --------------------------------------------------------

        if "Popularity" in df.columns:

            df = df.sort_values(
                by="Popularity",
                ascending=False
            )

        # --------------------------------------------------------
        # Reset index
        # --------------------------------------------------------

        df.reset_index(
            drop=True,
            inplace=True
        )

        # --------------------------------------------------------
        # Save individual processed dataset
        # --------------------------------------------------------

        output_file = (
            PROCESSED_FOLDER /
            f"top_tracks_{time_range}_clean.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"Saved {output_file.name}"
        )

        transformed_dfs[time_range] = df

    # ------------------------------------------------------------
    # Use 6 Months as the main Top Tracks dataset
    # ------------------------------------------------------------

    if "medium_term" in transformed_dfs:

        main_df = transformed_dfs["medium_term"].copy()

        main_df.to_csv(
            PROCESSED_FOLDER /
            "top_tracks_clean.csv",
            index=False
        )

        print(
            "Saved top_tracks_clean.csv "
            "(6 Months)"
        )

    print("\n✓ Top Tracks transformed")

    return transformed_dfs


# ============================================================
# TOP ARTISTS
# ============================================================

def transform_artists():

    print("\nTransforming Top Artists...")

    time_ranges = {
        "short_term": "4 Weeks",
        "medium_term": "6 Months",
        "long_term": "All Time"
    }

    transformed_dfs = {}

    for time_range, label in time_ranges.items():

        print(
            f"\nTransforming Top Artists — "
            f"{time_range}..."
        )

        input_file = (
            RAW_FOLDER /
            f"top_artists_{time_range}.csv"
        )

        if not input_file.exists():

            print(
                f"Skipping {time_range}: "
                f"{input_file.name} not found"
            )

            continue

        df = pd.read_csv(input_file)

        # --------------------------------------------------------
        # Remove duplicates and invalid rows
        # --------------------------------------------------------

        df = df.drop_duplicates()

        df = df.dropna(
            subset=["Artist Name"]
        )

        # --------------------------------------------------------
        # Fix encoding
        # --------------------------------------------------------

        if "Artist Name" in df.columns:

            df["Artist Name"] = (
                df["Artist Name"]
                .apply(fix_encoding)
            )

        # --------------------------------------------------------
        # Add Time Range
        # --------------------------------------------------------

        df["Time Range"] = label

        # --------------------------------------------------------
        # Remove unusable columns
        # --------------------------------------------------------

        df.drop(
            columns=[
                "Followers",
                "Genres",
                "Popularity"
            ],
            errors="ignore",
            inplace=True
        )

        # --------------------------------------------------------
        # Reset index
        # --------------------------------------------------------

        df.reset_index(
            drop=True,
            inplace=True
        )

        # --------------------------------------------------------
        # Save individual processed dataset
        # --------------------------------------------------------

        output_file = (
            PROCESSED_FOLDER /
            f"top_artists_{time_range}_clean.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"Saved {output_file.name}"
        )

        transformed_dfs[time_range] = df

    # ------------------------------------------------------------
    # Use 6 Months as the main Top Artists dataset
    # ------------------------------------------------------------

    if "medium_term" in transformed_dfs:

        main_df = transformed_dfs["medium_term"].copy()

        main_df.to_csv(
            PROCESSED_FOLDER /
            "top_artists_clean.csv",
            index=False
        )

        print(
            "Saved top_artists_clean.csv "
            "(6 Months)"
        )

    print("\n✓ Top Artists transformed")

    return transformed_dfs


# ============================================================
# PLAYLISTS
# ============================================================

def transform_playlists():

    print("\nTransforming Playlists...")

    input_file = RAW_FOLDER / "playlists.csv"

    if not input_file.exists():

        print("playlists.csv not found")

        return None

    df = pd.read_csv(input_file)

    # ------------------------------------------------------------
    # Remove duplicates and invalid rows
    # ------------------------------------------------------------

    df = df.drop_duplicates()

    df = df.dropna(
        subset=["Playlist Name"]
    )

    # ------------------------------------------------------------
    # Fix encoding
    # ------------------------------------------------------------

    if "Playlist Name" in df.columns:

        df["Playlist Name"] = (
            df["Playlist Name"]
            .apply(fix_encoding)
        )

    if "Owner" in df.columns:

        df["Owner"] = (
            df["Owner"]
            .apply(fix_encoding)
        )

    # ------------------------------------------------------------
    # Convert track count
    # ------------------------------------------------------------

    if "Tracks" in df.columns:

        df["Tracks"] = (
            df["Tracks"]
            .fillna(0)
            .astype(int)
        )

    # ------------------------------------------------------------
    # Remove unnecessary column
    # ------------------------------------------------------------

    df.drop(
        columns=["Collaborative"],
        errors="ignore",
        inplace=True
    )

    # ------------------------------------------------------------
    # Sort by number of tracks
    # ------------------------------------------------------------

    if "Tracks" in df.columns:

        df = df.sort_values(
            by="Tracks",
            ascending=False
        )

    # ------------------------------------------------------------
    # Reset index
    # ------------------------------------------------------------

    df.reset_index(
        drop=True,
        inplace=True
    )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    df.to_csv(
        PROCESSED_FOLDER /
        "top_playlists_clean.csv",
        index=False
    )

    print(
        "Saved top_playlists_clean.csv"
    )

    print("✓ Playlists transformed")

    return df


# ============================================================
# RECENTLY PLAYED
# ============================================================

def transform_recently_played():

    print("\nTransforming Recently Played...")

    input_file = (
        RAW_FOLDER /
        "recently_played.csv"
    )

    if not input_file.exists():

        print("recently_played.csv not found")

        return None

    df = pd.read_csv(input_file)

    # ------------------------------------------------------------
    # Remove duplicates and invalid rows
    # ------------------------------------------------------------

    df = df.drop_duplicates()

    df = df.dropna(
        subset=["Track Name"]
    )

    # ------------------------------------------------------------
    # Fix encoding
    # ------------------------------------------------------------

    for column in [
        "Track Name",
        "Artist",
        "Album"
    ]:

        if column in df.columns:

            df[column] = (
                df[column]
                .apply(fix_encoding)
            )

    # ============================================================
    # UTC → INDIA STANDARD TIME
    # ============================================================

    df["Played At UTC"] = pd.to_datetime(
        df["Played At"],
        errors="coerce",
        utc=True
    )

    df["Played At IST"] = (
        df["Played At UTC"]
        .dt.tz_convert("Asia/Kolkata")
    )

    # ============================================================
    # DATE / TIME COLUMNS
    # ============================================================

    df["Played Date"] = (
        df["Played At IST"]
        .dt.strftime("%Y-%m-%d")
    )

    df["Played Time"] = (
        df["Played At IST"]
        .dt.strftime("%H:%M:%S")
    )

    df["Hour Played"] = (
        df["Played At IST"]
        .dt.hour
    )

    df["Hour Label"] = (
        df["Played At IST"]
        .dt.strftime("%I %p")
        .str.lstrip("0")
        .str.strip()
    )

    # ============================================================
    # DAY INFORMATION
    # ============================================================

    df["Day Name"] = (
        df["Played At IST"]
        .dt.day_name()
    )

    df["Weekday Number"] = (
        df["Played At IST"]
        .dt.weekday
    )

    # ============================================================
    # DURATION
    # ============================================================

    if "Duration_ms" in df.columns:

        df["Duration (Minutes)"] = (
            df["Duration_ms"] / 60000
        ).round(2)

    # ============================================================
    # REMOVE RAW / UNNECESSARY COLUMNS
    # ============================================================

    df.drop(
        columns=[
            "Played At",
            "Played At UTC",
            "Played At IST",
            "Duration_ms",
            "Popularity",
            "Preview URL"
        ],
        errors="ignore",
        inplace=True
    )

    # ============================================================
    # RESET INDEX
    # ============================================================

    df.reset_index(
        drop=True,
        inplace=True
    )

    # ============================================================
    # SAVE
    # ============================================================

    df.to_csv(
        PROCESSED_FOLDER /
        "recently_played_clean.csv",
        index=False
    )

    print(
        "Saved recently_played_clean.csv"
    )

    print("✓ Recently Played transformed")

    return df


# ============================================================
# TRACK — ARTIST BRIDGE
# ============================================================

def create_track_artist_bridge():

    print("\nCreating Track-Artist Bridge...")

    input_file = (
        PROCESSED_FOLDER /
        "top_tracks_clean.csv"
    )

    if not input_file.exists():

        print(
            "top_tracks_clean.csv not found"
        )

        return None

    df = pd.read_csv(input_file)

    bridge_rows = []

    for _, row in df.iterrows():

        track_id = row.get("Track ID")

        artist_ids_raw = str(
            row.get("Artist IDs", "")
        )

        artist_names_raw = str(
            row.get("Artists", "")
        )

        artist_ids = [
            artist.strip()
            for artist in artist_ids_raw.split(",")
        ]

        artist_names = [
            artist.strip()
            for artist in artist_names_raw.split(",")
        ]

        for artist_id, artist_name in zip(
            artist_ids,
            artist_names
        ):

            bridge_rows.append({
                "Track ID": track_id,
                "Artist ID": artist_id,
                "Artist Name": artist_name
            })

    bridge_df = pd.DataFrame(
        bridge_rows
    )

    if not bridge_df.empty:

        bridge_df = (
            bridge_df
            .drop_duplicates()
            .sort_values(
                ["Track ID", "Artist Name"]
            )
        )

        bridge_df.reset_index(
            drop=True,
            inplace=True
        )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    bridge_df.to_csv(
        PROCESSED_FOLDER /
        "bridge_track_artist.csv",
        index=False
    )

    print(
        "Saved bridge_track_artist.csv"
    )

    return bridge_df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    transform_tracks()

    transform_artists()

    transform_playlists()

    transform_recently_played()

    create_track_artist_bridge()