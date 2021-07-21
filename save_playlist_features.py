import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

load_dotenv()

scope = "playlist-modify-public playlist-modify-private user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist = os.getenv("PLAYLIST")

# get length of playlist
playlist_len = sp.playlist(playlist_id=playlist)["tracks"]["total"]

# read result in chunks of 100
results = {
    "items": [],
}
for i in range(0, playlist_len, 100):
    new_results = sp.playlist_items(fields=["items"], playlist_id=playlist, limit=100, offset=i)
    results["items"].extend(new_results["items"])

for idx, item in enumerate(results["items"], 1):
    track = item["track"]
    print(idx, track["artists"][0]["name"], " – ", track["name"])

# get all track uri's from results
track_uris = list(map(lambda item: item["track"]["uri"], results["items"]))
features = []
# get features for each track in chuncks of 100
for i in range(0, len(track_uris), 100):
    features.extend(sp.audio_features(track_uris[i:i+100]))

# save track features to csv
with open("spotify_features.csv", "w") as csvfile:
    fieldnames = [
        "idx",
        "name",
        "uri",
        "key",
        "mode",
        "danceability",
        "energy",
        "loudness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for idx, item in enumerate(results["items"], 1):
        track = item["track"]
        feature = features[idx - 1]
        writer.writerow(
            {
                "idx": idx,
                "name": track["name"],
                "uri": track["uri"],
                "key": feature["key"],
                "mode": feature["mode"],
                "danceability": feature["danceability"],
                "energy": feature["energy"],
                "loudness": feature["loudness"],
                "acousticness": feature["acousticness"],
                "instrumentalness": feature["instrumentalness"],
                "liveness": feature["liveness"],
                "valence": feature["valence"],
                "tempo": feature["tempo"],
            }
        )
