import pandas as pd
import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# --------------------------------
# Load dataset
# --------------------------------

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

# --------------------------------
# Feature engineering
# --------------------------------

df["depth_missing"] = df["earthquake_depth_km"].isna().astype(int)
df["elevation_missing"] = df["elevation_m"].isna().astype(int)

depth = df["earthquake_depth_km"].fillna(
    df["earthquake_depth_km"].median()
)

elevation = df["elevation_m"].fillna(
    df["elevation_m"].median()
)

distance = df["distance_to_epicenter_km"]
magnitude = df["earthquake_magnitude"]

df["magnitude_distance_ratio"] = (
    magnitude / (distance + 1)
)

df["magnitude_distance_interaction"] = (
    magnitude * distance
)

df["depth_distance_ratio"] = (
    depth / (distance + 1)
)

df["log_elevation"] = np.log1p(elevation)

# --------------------------------
# Final P1 features
# --------------------------------

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

X = df[features]
y = df["label"]

# --------------------------------
# Final P1 model
# --------------------------------

p1_model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

# Train on complete dataset
p1_model.fit(X, y)

# --------------------------------
# Save model
# --------------------------------

joblib.dump(
    p1_model,
    r"models\p1_ground_failure_model.joblib"
)

# Save feature list
with open("p1_features.txt", "w") as f:
    for feature in features:
        f.write(feature + "\n")

print("===================================")
print("FINAL P1 MODEL TRAINED")
print("===================================")
print("Model : Logistic Regression")
print("Samples:", len(X))
print("Features:", len(features))
print("\nFeatures used:")

for feature in features:
    print("-", feature)

print("\nSaved files:")
print(r"models\p1_ground_failure_model.joblib")
print("p1_features.txt")
