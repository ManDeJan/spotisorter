import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

load_dotenv()

scope = "playlist-modify-public playlist-modify-private user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist = os.getenv("PLAYLIST")

user = sp.current_user()
results = sp.user_playlist_tracks(user, playlist_id=playlist)

for idx, item in enumerate(results["items"], 1):
    track = item["track"]
    print(idx, track["artists"][0]["name"], " – ", track["name"])

# get all track uri's from results
track_uris = list(map(lambda item: item["track"]["uri"], results["items"]))
features = sp.audio_features(track_uris)

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
