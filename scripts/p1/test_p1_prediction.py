import pandas as pd
import joblib
import numpy as np

# Load model
model = joblib.load(r"models\p1_ground_failure_model.joblib")

# Load dataset
df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

# Take one existing sample
sample = df.iloc[[0]].copy()

# Feature engineering
sample["depth_missing"] = sample["earthquake_depth_km"].isna().astype(int)
sample["elevation_missing"] = sample["elevation_m"].isna().astype(int)

depth = sample["earthquake_depth_km"].fillna(
    df["earthquake_depth_km"].median()
)

elevation = sample["elevation_m"].fillna(
    df["elevation_m"].median()
)

distance = sample["distance_to_epicenter_km"]
magnitude = sample["earthquake_magnitude"]

sample["magnitude_distance_ratio"] = (
    magnitude / (distance + 1)
)

sample["magnitude_distance_interaction"] = (
    magnitude * distance
)

sample["depth_distance_ratio"] = (
    depth / (distance + 1)
)

sample["log_elevation"] = np.log1p(elevation)

# Exact feature order
features = [
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

X = sample[features]

# Prediction
prediction = model.predict(X)[0]
probability = model.predict_proba(X)[0][1]

print("===================================")
print("P1 PREDICTION TEST")
print("===================================")

print("Predicted class:", prediction)
print("Ground-failure probability:",
      round(probability, 4))

if prediction == 1:
    print("Prediction: LANDSLIDE")
else:
    print("Prediction: BACKGROUND")
