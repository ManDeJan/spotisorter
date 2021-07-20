import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_simulated_annealing
from itertools import combinations

import csv

filename = "spotify_features.csv"


def try_type(value):
    """try to convert to float or int else return string"""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


# turn the csv into a dict with keys from first row
with open(filename, "r") as csvfile:
    reader = csv.reader(csvfile)
    header, *tracks = list(reader)
    tracks = [
        dict(zip(map(lambda h: h.strip(), header), map(try_type, track)))
        for track in tracks
    ]

# get min and max tempo
min_tempo, max_tempo = min(map(lambda track: track["tempo"], tracks)), max(
    map(lambda track: track["tempo"], tracks)
)


def distance_function(track1, track2):
    """Calculate distance based on key, mode, energy, valence, danceability, tempo and loudness"""
    # get key and mode for both tracks
    same_mode = track1["mode"] == track2["mode"]
    key1 = track1["key"]
    key2 = track2["key"]
    # calculate distance based on key and mode
    if same_mode:
        key_diff = min(abs(key1 - key2), 12 - abs(key1 - key2))
        if key_diff == 6:
            key_distance = 0.5
        elif key_diff <= 1:
            key_distance = 0
        elif key_diff <= 2:
            key_distance = 0.5
        else:
            key_distance = 1
    else:
        key_distance = 0 if key1 == key2 else 1

    # map tempo from min_tempo to max_tempo to 0 to 1
    tempo1 = (track1["tempo"] - min_tempo) / (max_tempo - min_tempo)
    tempo2 = (track2["tempo"] - min_tempo) / (max_tempo - min_tempo)
    tempo_distance = abs(tempo1 - tempo2)

    # map loudness from -60 to 0 to 0 to 1
    loudness1 = (track1["loudness"] - -60) / (0 - -60)
    loudness2 = (track2["loudness"] - -60) / (0 - -60)
    loudness_distance = abs(loudness1 - loudness2)

    # energy valance, danceability distances
    energy_distance = abs(track1["energy"] - track2["energy"])
    valence_distance = abs(track1["valence"] - track2["valence"])
    danceability_distance = abs(track1["danceability"] - track2["danceability"])

    weights = {
        "key_weight": 3,
        "tempo_weight": 0,
        "loudness_weight": 0,
        "energy_weight": 3,
        "valence_weight": 4,
        "danceability_weight": 2,
    }
    # multiply distances with weights
    song_distance = sum(
        map(
            lambda x: weights[x[0]] * x[1],
            zip(
                weights.keys(),
                [
                    key_distance,
                    tempo_distance,
                    loudness_distance,
                    energy_distance,
                    valence_distance,
                    danceability_distance,
                ],
            ),
        )
    )
    globals().update(locals())
    return song_distance


# calculate the distance matrix
distances = np.array(
    [[distance_function(track1, track2) for track2 in tracks] for track1 in tracks]
)
distances[:, 0] = 0  # open ended problem

# solve with solve_tsp_simulated_annealing
permutation, distance = solve_tsp_simulated_annealing(distances, alpha=0.999)
# save the track name with the old and new order; key, mode, energy, valence, danceability, tempo and loudness to a csv
with open("sorted_tracks.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        [
            "track",
            "uri",
            "old_order",
            "new_order",
            "key",
            "mode",
            "energy",
            "valence",
            "danceability",
            "tempo",
            "loudness",
        ]
    )
    for new_pos, i in enumerate(permutation):
        track = tracks[i]
        writer.writerow(
            [
                track["name"],
                track["uri"],
                tracks.index(tracks[i]) + 1,
                new_pos + 1,
                track["key"],
                track["mode"],
                track["energy"],
                track["valence"],
                track["danceability"],
                track["tempo"],
                track["loudness"],
            ]
        )

for i, j in zip(permutation, permutation[1:]):
    print(tracks[i]["name"], "-->", tracks[j]["name"])

# divide distance by sum of weights
normalized_distance = distance / sum(weights.values())
avg_distance_per_track = normalized_distance / len(tracks)

print(f"norm_dist: {normalized_distance}\navg_dist_per_track: {avg_distance_per_track}")
