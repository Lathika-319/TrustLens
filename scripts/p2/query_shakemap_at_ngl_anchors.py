import json
import math
import os
import pandas as pd
import numpy as np


ANCHOR_FILE = r"outputs\verified_ngl_anchors.csv"
CACHE_DIR = r"data\raw\shakemap_cache"
OUT = r"outputs\verified_ngl_anchor_pga_direct.csv"


SHAKEMAP_FILES = {
    "Kobe": "usp0006rew_pga.covjson",
    "Niigata-Chuetsu": "usp000d6vk_pga.covjson",
    "Tohoku-Oki": "official20110311054624120_30_pga.covjson",
}


def load_covjson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def get_pga_grid(covjson):
    axes = covjson["domain"]["axes"]

    x = axes["x"]
    y = axes["y"]

    lon_values = np.linspace(
        x["start"],
        x["stop"],
        x["num"],
    )

    lat_values = np.linspace(
        y["start"],
        y["stop"],
        y["num"],
    )

    values = covjson["ranges"]["PGA"]["values"]

    return lon_values, lat_values, values


def nearest_grid_value(
    anchor_lat,
    anchor_lon,
    lon_values,
    lat_values,
    values,
):
    n_lon = len(lon_values)
    n_lat = len(lat_values)

    if len(values) != n_lon * n_lat:
        raise ValueError(
            f"Grid size mismatch: "
            f"{n_lon} x {n_lat} = {n_lon*n_lat}, "
            f"but PGA values = {len(values)}"
        )

    best = None

    for iy, lat in enumerate(lat_values):

        for ix, lon in enumerate(lon_values):

            idx = iy * n_lon + ix

            value = values[idx]

            if value is None:
                continue

            distance = haversine_km(
                anchor_lat,
                anchor_lon,
                lat,
                lon,
            )

            if best is None or distance < best["distance_km"]:

                best = {
                    "grid_latitude": float(lat),
                    "grid_longitude": float(lon),
                    "grid_value": value,
                    "distance_km": distance,
                }

    return best


anchors = pd.read_csv(ANCHOR_FILE)

rows = []

for scenario, filename in SHAKEMAP_FILES.items():

    path = os.path.join(CACHE_DIR, filename)

    print(f"\nLoading {scenario}:")
    print(path)

    covjson = load_covjson(path)

    lon_values, lat_values, values = get_pga_grid(covjson)

    print(
        "Grid:",
        len(lon_values),
        "x",
        len(lat_values),
        "cells:",
        len(values),
    )

    subset = anchors[
        anchors["scenario"] == scenario
    ]

    for _, anchor in subset.iterrows():

        result = nearest_grid_value(
            anchor["latitude"],
            anchor["longitude"],
            lon_values,
            lat_values,
            values,
        )

        rows.append(
            {
                "scenario": scenario,
                "anchor_group": anchor["anchor_group"],
                "ngl_site": anchor["ngl_site"],
                "match_level": anchor["match_level"],
                "anchor_latitude": anchor["latitude"],
                "anchor_longitude": anchor["longitude"],
                "anchor_epicenter_distance_km": anchor[
                    "distance_to_epicenter_km"
                ],
                "shakemap_grid_latitude": result[
                    "grid_latitude"
                ],
                "shakemap_grid_longitude": result[
                    "grid_longitude"
                ],
                "shakemap_anchor_distance_km": result[
                    "distance_km"
                ],
                "shakemap_pga_raw": result[
                    "grid_value"
                ],
            }
        )


df = pd.DataFrame(rows)

print("\n================================")
print("DIRECT SHAKEMAP ANCHOR RESULTS")
print("================================")

print(
    df[
        [
            "scenario",
            "anchor_group",
            "ngl_site",
            "shakemap_anchor_distance_km",
            "shakemap_pga_raw",
        ]
    ].to_string(index=False)
)

df.to_csv(OUT, index=False)

print("\nSaved:", OUT)