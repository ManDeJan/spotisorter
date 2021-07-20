import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
import os

load_dotenv()

scope = "playlist-modify-public playlist-modify-private user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# get playlist from .env
playlist = os.getenv("PLAYLIST")

user = sp.current_user()
results = sp.user_playlist_tracks(user, playlist_id=playlist)

# open sorted_tracks.csv and read into a list, sort on new_order
with open("sorted_tracks.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    # read tracks zip with header
    header, *rows = reader
    tracks = [dict(zip(header, row)) for row in rows]

    # update old_order with old_order from results["items"]
    old_orders = list(map(lambda i: i["track"]["uri"], results["items"]))
    for track in tracks:
        track["old_order"] = old_orders.index(track["uri"])

    tracks = sorted(tracks, key=lambda x: int(x["old_order"]))

new_orders = [int(track["new_order"]) - 1 for track in tracks]

# use new orders to reorder item into the right order
for i in range(len(new_orders)):
    track_to_be_moved = new_orders.index(i)
    if i == track_to_be_moved:
        continue
    sp.playlist_reorder_items(playlist, track_to_be_moved, i)
    new_orders.insert(i, new_orders.pop(track_to_be_moved))
    sleep(0.1)  # be a good internet citizen
