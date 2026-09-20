import pandas as pd
import joblib

# =========================
# LOAD P1 DATA + MODEL
# =========================

p1_file = r"data\raw\QuakeShield_Final_Dataset.csv"
p1_df = pd.read_csv(p1_file)

p1_model = joblib.load(r"models\p1_ground_failure_model.joblib")

# P1 features
p1_features = [
    "earthquake_magnitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m"
]

# Create P1 missing indicators
p1_df["depth_missing"] = p1_df["earthquake_depth_km"].isna().astype(int)
p1_df["elevation_missing"] = p1_df["elevation_m"].isna().astype(int)

# Median values for feature engineering
depth_median = p1_df["earthquake_depth_km"].median()
elevation_median = p1_df["elevation_m"].median()

depth = p1_df["earthquake_depth_km"].fillna(depth_median)
elevation = p1_df["elevation_m"].fillna(elevation_median)
distance = p1_df["distance_to_epicenter_km"]
magnitude = p1_df["earthquake_magnitude"]

p1_df["magnitude_distance_ratio"] = magnitude / (distance + 1)
p1_df["magnitude_distance_interaction"] = magnitude * distance
p1_df["depth_distance_ratio"] = depth / (distance + 1)
p1_df["log_elevation"] = __import__("numpy").log1p(elevation)

p1_features_final = [
    "earthquake_magnitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m",
    "depth_missing",
    "elevation_missing",
    "magnitude_distance_ratio",
    "magnitude_distance_interaction",
    "depth_distance_ratio",
    "log_elevation"
]

p1_X = p1_df[p1_features_final]

p1_df["P1_ground_failure_probability"] = p1_model.predict_proba(p1_X)[:, 1]


# =========================
# LOAD P2 DATA + MODEL
# =========================

p2_file = r"data\raw\Database 7.xlsx"
p2_df = pd.read_excel(p2_file)

p2_model = joblib.load(r"models\p2_liquefaction_model.joblib")

# Convert FC to numeric
p2_df["FC (%)"] = pd.to_numeric(
    p2_df["FC (%)"],
    errors="coerce"
)

missing_columns = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for col in missing_columns:
    p2_df[col + "_missing"] = p2_df[col].isna().astype(int)

p2_features = [
    "σv/σv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)",
    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"
]

p2_X = p2_df[p2_features]

p2_df["P2_liquefaction_probability"] = (
    p2_model.predict_proba(p2_X)[:, 1]
)


# =========================
# SAVE RISK INPUTS
# =========================

p1_output = p1_df[
    [
        "earthquake_id",
        "earthquake_name",
        "earthquake_date",
        "latitude",
        "longitude",
        "P1_ground_failure_probability"
    ]
].copy()

p2_output = p2_df[
    [
        "Country",
        "Region",
        "Site",
        "Mw",
        "PGA(g)",
        "P2_liquefaction_probability"
    ]
].copy()

p1_output.to_csv(
    "p1_prediction_outputs.csv",
    index=False
)

p2_output.to_csv(
    "p2_prediction_outputs.csv",
    index=False
)

print("=" * 60)
print("RISK FUSION INPUT GENERATION COMPLETED")
print("=" * 60)

print("\nP1 prediction rows:", len(p1_output))
print("P2 prediction rows:", len(p2_output))

print("\nP1 probability range:")
print(
    round(p1_output["P1_ground_failure_probability"].min(), 4),
    "to",
    round(p1_output["P1_ground_failure_probability"].max(), 4)
)

print("\nP2 probability range:")
print(
    round(p2_output["P2_liquefaction_probability"].min(), 4),
    "to",
    round(p2_output["P2_liquefaction_probability"].max(), 4)
)

print("\nSaved:")
print("p1_prediction_outputs.csv")
print("p2_prediction_outputs.csv")
