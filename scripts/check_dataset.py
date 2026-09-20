import pandas as pd

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

features = [
    "latitude",
    "longitude",
    "earthquake_magnitude",
    "earthquake_latitude",
    "earthquake_longitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m"
]

print("Correlation of P1 features with label")
print("=" * 60)

print(df[features + ["label"]].corr()["label"].sort_values(ascending=False))
