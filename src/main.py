from spotify_client import get_spotify_client
from extract.tracks import extract_top_tracks
from extract.artists import extract_top_artists
from extract.playlists import extract_playlists
from extract.recent import extract_recently_played

from transform import (
    transform_tracks,
    transform_artists,
    transform_playlists,
    transform_recently_played,
)
def main():

    print("=" * 50)
    print("Spotify ETL Pipeline")
    print("=" * 50)

    sp = get_spotify_client()

    extract_top_tracks(sp)
    extract_top_artists(sp)
    extract_playlists(sp)
    extract_recently_played(sp)

    print("\nStarting Transform Phase...\n")

    transform_tracks()
    transform_artists()
    transform_playlists()
    transform_recently_played()

    print("\nFinished!")


if __name__ == "__main__":
    main()