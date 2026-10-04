import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

DATA = r"data\QuakeShield_Final_Dataset_Slope.csv"

df = pd.read_csv(DATA)

print("=" * 100)
print("BACKGROUND LABEL QUALITY AUDIT")
print("=" * 100)

bands = [
    ("<2km", 0, 2),
    ("2-5km", 2, 5),
    ("5-10km", 5, 10),
    (">10km", 10, np.inf),
]

print()
print(
    "event,band,n,mean_slope,median_slope,"
    "mean_elevation,median_elevation"
)

all_results = []

for event_name, group in df.groupby("earthquake_name"):

    positives = group[group["label"] == 1].copy()
    backgrounds = group[group["label"] == 0].copy()

    if len(positives) == 0 or len(backgrounds) == 0:
        continue

    # Latitude/longitude are converted approximately to km.
    # 1 degree latitude ≈ 111.32 km.
    pos_coords = positives[["latitude", "longitude"]].to_numpy()
    bg_coords = backgrounds[["latitude", "longitude"]].to_numpy()

    nn = NearestNeighbors(
        n_neighbors=1,
        metric="euclidean"
    )

    nn.fit(pos_coords)

    distances_deg, _ = nn.kneighbors(bg_coords)

    distances_km = distances_deg[:, 0] * 111.32

    backgrounds = backgrounds.copy()
    backgrounds["nearest_positive_km"] = distances_km

    for band_name, lower, upper in bands:

        mask = (
            (backgrounds["nearest_positive_km"] >= lower)
            & (backgrounds["nearest_positive_km"] < upper)
        )

        g = backgrounds.loc[mask]

        if len(g) == 0:
            continue

        result = {
            "event": event_name,
            "band": band_name,
            "n": len(g),
            "mean_slope": g["slope_degrees"].mean(),
            "median_slope": g["slope_degrees"].median(),
            "mean_elevation": g["elevation_m"].mean(),
            "median_elevation": g["elevation_m"].median(),
        }

        all_results.append(result)

        print(
            f"{event_name},"
            f"{band_name},"
            f"{len(g)},"
            f"{g['slope_degrees'].mean():.2f},"
            f"{g['slope_degrees'].median():.2f},"
            f"{g['elevation_m'].mean():.2f},"
            f"{g['elevation_m'].median():.2f}"
        )

print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)

results = pd.DataFrame(all_results)

if not results.empty:

    summary = (
        results
        .groupby("band")
        .agg(
            total_background_cells=("n", "sum"),
            mean_slope=("mean_slope", "mean"),
            median_slope=("median_slope", "median"),
            mean_elevation=("mean_elevation", "mean"),
            median_elevation=("median_elevation", "median"),
        )
    )

    print(summary.round(2))

print()
print("=" * 100)
print("AUDIT COMPLETE")
print("=" * 100)
