import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

# Missing indicators
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

# Feature engineering
df["magnitude_distance_ratio"] = magnitude / (distance + 1)
df["magnitude_distance_interaction"] = magnitude * distance
df["depth_distance_ratio"] = depth / (distance + 1)
df["log_elevation"] = np.log1p(elevation)

features = [
    "earthquake_magnitude",
    "earthquake_latitude",
    "earthquake_longitude",
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
groups = df["earthquake_id"]

gkf = GroupKFold(n_splits=5)

fold = 1

for train_idx, test_idx in gkf.split(X, y, groups):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    test_events = df.iloc[test_idx]["earthquake_id"].unique()

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", GradientBoostingClassifier(random_state=42))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 50)
    print(f"FOLD {fold}")
    print("=" * 50)

    print("Test earthquake event(s):")
    for event in test_events:
        print(" ", event)

    print("\nTest samples:", len(test_idx))
    print("Actual background:", (y_test == 0).sum())
    print("Actual landslide :", (y_test == 1).sum())

    print("\nMetrics:")
    print("Accuracy :", round(accuracy_score(y_test, y_pred), 4))
    print("Precision:", round(
        precision_score(y_test, y_pred, zero_division=0), 4
    ))
    print("Recall   :", round(
        recall_score(y_test, y_pred, zero_division=0), 4
    ))
    print("F1       :", round(
        f1_score(y_test, y_pred, zero_division=0), 4
    ))
    print("ROC-AUC  :", round(
        roc_auc_score(y_test, y_prob), 4
    ))

    print("\nPredicted classes:")
    print(" Predicted background:", (y_pred == 0).sum())
    print(" Predicted landslide :", (y_pred == 1).sum())

    fold += 1
