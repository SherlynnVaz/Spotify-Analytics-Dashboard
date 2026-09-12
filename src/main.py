from spotify_client import get_spotify_client

from extract.tracks import extract_top_tracks
from extract.artists import extract_top_artists
from extract.playlists import extract_playlists
from extract.recent import extract_recently_played

from create_sample_data import create_sample_data

from transform import (
    transform_tracks,
    transform_artists,
    transform_playlists,
    transform_recently_played,
)

from visualize import create_dashboard


def main():

    print("=" * 60)
    print("Spotify Analytics ETL Pipeline")
    print("=" * 60)

    # ========================================================
    # GET SPOTIFY CLIENT
    # ========================================================

    sp = get_spotify_client()


    # ========================================================
    # 1. EXTRACTION
    # ========================================================

    print("\n[1/4] Starting Extraction Phase...\n")

    extract_top_tracks(sp)
    extract_top_artists(sp)
    extract_playlists(sp)
    extract_recently_played(sp)

    print("\nExtraction Complete!")


    # ========================================================
    # 2. TRANSFORMATION
    # ========================================================

    print("\n[2/4] Starting Transformation Phase...\n")

    transform_tracks()
    transform_artists()
    transform_playlists()
    transform_recently_played()

    print("\nTransformation Complete!")


    # ========================================================
    # 3. CREATE SAMPLE DATA
    # ========================================================

    print("\n[3/4] Creating Sample Dataset...\n")

    create_sample_data()

    print("\nSample Dataset Created!")


    # ========================================================
    # 4. CREATE VISUALIZATION
    # ========================================================

    print("\n[4/4] Creating Dashboard...\n")

    create_dashboard()

    print("\nDashboard Created!")


    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print("\n" + "=" * 60)
    print("ETL Pipeline Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()