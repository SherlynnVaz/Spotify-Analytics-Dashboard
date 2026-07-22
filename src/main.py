from spotify_client import get_spotify_client
from extract import extract_top_tracks

print("=" * 50)
print("Spotify ETL Pipeline")
print("=" * 50)

sp = get_spotify_client()

extract_top_tracks(sp)

print("\nFinished!")