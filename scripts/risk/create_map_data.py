import pandas as pd

# Load final risk scores
df = pd.read_csv("final_risk_scores.csv")

# Create frontend/map-ready dataset
map_data = df[
    [
        "earthquake_id",
        "earthquake_name",
        "earthquake_date",
        "latitude",
        "longitude",
        "earthquake_magnitude",
        "P1_ground_failure_probability",
        "mean_P2_liquefaction_probability",
        "final_risk_score",
        "risk_level"
    ]
].copy()

# Rename columns for easier frontend use
map_data = map_data.rename(columns={
    "earthquake_name": "location_name",
    "earthquake_magnitude": "magnitude",
    "P1_ground_failure_probability": "ground_failure_probability",
    "mean_P2_liquefaction_probability": "liquefaction_probability"
})

# Save
output_file = "quakeshield_map_data.csv"

map_data.to_csv(output_file, index=False)

print("=" * 70)
print("QUAKESHIELD MAP DATA CREATED")
print("=" * 70)

print("\nLocations:", len(map_data))

print("\nColumns:")
print(list(map_data.columns))

print("\nMap-ready data:")
print(map_data.to_string(index=False))

print("\nSaved:")
print(output_file)
