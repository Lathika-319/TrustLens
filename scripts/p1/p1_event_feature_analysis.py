import pandas as pd

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

features = [
    "earthquake_magnitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m"
]

for event, group in df.groupby("earthquake_id"):

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("=" * 70)

    print(
        group.groupby("label")[features]
        .mean()
        .rename(index={
            0: "background",
            1: "landslide"
        })
        .round(3)
    )
