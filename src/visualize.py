import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "visualizations"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# CREATE DASHBOARD
# ============================================================

def create_dashboard():

    # ========================================================
    # LOAD DATA
    # ========================================================

    tracks = pd.read_csv(
        PROCESSED_FOLDER / "top_tracks_clean.csv"
    )

    artists = pd.read_csv(
        PROCESSED_FOLDER / "top_artists_clean.csv"
    )

    playlists = pd.read_csv(
        PROCESSED_FOLDER / "top_playlists_clean.csv"
    )

    recently_played = pd.read_csv(
        PROCESSED_FOLDER / "recently_played_clean.csv"
    )

    bridge_track_artist = pd.read_csv(
        PROCESSED_FOLDER / "bridge_track_artist.csv"
    )


    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    print("\n================ DATASET INFORMATION ================\n")

    print("Top Tracks:")
    print(tracks.shape)

    print("\nTop Artists:")
    print(artists.shape)

    print("\nTop Playlists:")
    print(playlists.shape)

    print("\nRecently Played:")
    print(recently_played.shape)

    print("\nTrack-Artist Bridge:")
    print(bridge_track_artist.shape)


    # ========================================================
    # BASIC DATA PREPARATION
    # ========================================================

    # Make duration numeric
    if "Duration (Minutes)" in tracks.columns:

        tracks["Duration (Minutes)"] = pd.to_numeric(
            tracks["Duration (Minutes)"],
            errors="coerce"
        )


    # Make Hour Played numeric
    if "Hour Played" in recently_played.columns:

        recently_played["Hour Played"] = pd.to_numeric(
            recently_played["Hour Played"],
            errors="coerce"
        )


    # ========================================================
    # CREATE DASHBOARD
    # ========================================================

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(16, 10)
    )

    fig.suptitle(
        "Spotify Listening Analytics",
        fontsize=22,
        fontweight="bold",
        y=0.98
    )


    # ========================================================
    # 1. TOP 10 TRACKS - RANKED DOT PLOT
    # ========================================================

    ax = axes[0, 0]

    top_tracks = (
        tracks
        .head(10)
        .copy()
    )

    # Rank 1 should appear at the top
    top_tracks = top_tracks.iloc[::-1]

    track_names = top_tracks["Track Name"].tolist()

    # Original Spotify ranks
    ranks = list(
        range(
            len(top_tracks),
            0,
            -1
        )
    )

    # Y positions
    y_positions = range(len(track_names))

    # Plot dots
    ax.scatter(
        ranks,
        y_positions,
        s=100
    )

    # Add rank labels
    for x, y in zip(ranks, y_positions):

        ax.text(
            x + 0.15,
            y,
            f"#{x}",
            va="center",
            fontsize=10,
            fontweight="bold"
        )


    ax.set_yticks(
        list(y_positions)
    )

    ax.set_yticklabels(
        track_names
    )

    ax.set_title(
        "Top 10 Tracks",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Spotify Rank"
    )

    ax.set_ylabel("")


    # Rank 1 on the left
    ax.set_xlim(
        0.5,
        10.8
    )

    ax.set_xticks(
        range(1, 11)
    )

    ax.grid(
        axis="x",
        alpha=0.2
    )

    ax.set_axisbelow(True)


    # ========================================================
    # 2. TOP ARTISTS
    # ========================================================

    ax = axes[0, 1]

    artist_counts = (
        bridge_track_artist["Artist Name"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    bars = ax.barh(
        artist_counts.index,
        artist_counts.values
    )

    ax.set_title(
        "Top Artists in Your Top Tracks",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Number of Tracks"
    )

    ax.set_ylabel("")


    # Add values
    for bar in bars:

        width = bar.get_width()

        ax.text(
            width + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            fontsize=9
        )


    ax.set_xlim(
        0,
        max(artist_counts.values) + 2
    )


    # ========================================================
    # 3. TRACK DURATION
    # ========================================================

    ax = axes[1, 0]

    duration_bins = [
        0,
        2,
        3,
        4,
        5,
        6,
        float("inf")
    ]

    duration_labels = [
        "< 2 min",
        "2–3 min",
        "3–4 min",
        "4–5 min",
        "5–6 min",
        "6+ min"
    ]

    tracks["Duration Bucket"] = pd.cut(
        tracks["Duration (Minutes)"],
        bins=duration_bins,
        labels=duration_labels,
        right=False
    )

    duration_counts = (
        tracks["Duration Bucket"]
        .value_counts()
        .reindex(duration_labels)
        .fillna(0)
    )

    bars = ax.bar(
        duration_counts.index,
        duration_counts.values,
        width=0.65
    )

    ax.set_title(
        "Track Duration Distribution",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Duration"
    )

    ax.set_ylabel(
        "Number of Tracks"
    )

    ax.tick_params(
        axis="x",
        rotation=25
    )


    # Add values
    for bar in bars:

        height = bar.get_height()

        if height > 0:

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.3,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9
            )


    # ========================================================
    # 4. RECENTLY PLAYED TRACKS BY HOUR
    # ========================================================

    ax = axes[1, 1]

    # --------------------------------------------------------
    # Count plays by hour
    # --------------------------------------------------------

    hour_counts = (
        recently_played["Hour Played"]
        .dropna()
        .astype(int)
        .value_counts()
    )


    # --------------------------------------------------------
    # Create all 24 hours
    # --------------------------------------------------------

    all_hours = pd.Series(
        0,
        index=range(24)
    )

    all_hours.update(
        hour_counts
    )


    # --------------------------------------------------------
    # Create readable hour labels
    # --------------------------------------------------------

    hour_labels = []

    for hour in range(24):

        if hour == 0:

            label = "12 AM"

        elif hour < 12:

            label = f"{hour} AM"

        elif hour == 12:

            label = "12 PM"

        else:

            label = f"{hour - 12} PM"

        hour_labels.append(label)


    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    bars = ax.bar(
        range(24),
        all_hours.values,
        width=0.7
    )

    ax.set_title(
        "Recently Played Tracks by Hour",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Time of Day"
    )

    ax.set_ylabel(
        "Number of Plays"
    )


    # Show every 2 hours
    ax.set_xticks(
        range(0, 24, 2)
    )

    ax.set_xticklabels(
        hour_labels[::2],
        rotation=45,
        ha="right"
    )


    # Add values only where plays exist
    for hour, bar in enumerate(bars):

        height = bar.get_height()

        if height > 0:

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.2,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=8
            )


    # ========================================================
    # GENERAL FORMATTING
    # ========================================================

    for ax in axes.flat:

        ax.grid(
            axis="y",
            alpha=0.2
        )

        ax.set_axisbelow(True)


    # ========================================================
    # LAYOUT
    # ========================================================

    plt.tight_layout(
        rect=[0, 0, 1, 0.95]
    )


    # ========================================================
    # SAVE DASHBOARD
    # ========================================================

    output_path = (
        OUTPUT_FOLDER /
        "spotify_analytics_dashboard.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


    print(
        "\n============================================================"
    )

    print(
        "Dashboard saved to:"
    )

    print(
        output_path
    )

    print(
        "============================================================"
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    create_dashboard()