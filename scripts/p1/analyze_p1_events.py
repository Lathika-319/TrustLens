import pandas as pd

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

print("\nP1 EVENT-WISE ANALYSIS")
print("=" * 80)

result = df.groupby("earthquake_id").agg(
    rows=("label", "size"),
    landslides=("label", "sum"),
    landslide_rate=("label", "mean"),
    magnitude=("earthquake_magnitude", "first"),
    depth_km=("earthquake_depth_km", "first"),
    avg_distance_km=("distance_to_epicenter_km", "mean"),
    avg_elevation_m=("elevation_m", "mean")
)

result["landslide_rate"] = result["landslide_rate"] * 100

print(result.round(3).to_string())

print("\n\nLABEL COUNTS BY EARTHQUAKE")
print("=" * 80)

counts = pd.crosstab(
    df["earthquake_id"],
    df["label_name"]
)

print(counts.to_string())
