import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score
)

DATA = r"TrustLens-push\data\QuakeShield_Final_Dataset_Slope.csv"
OUTPUT = r"TrustLens-push\outputs\p1_loeo_slope_results.csv"

df = pd.read_csv(DATA)


def make_features(d):

    X = pd.DataFrame(index=d.index)

    X["earthquake_magnitude"] = d["earthquake_magnitude"]
    X["earthquake_depth_km"] = d["earthquake_depth_km"]
    X["distance_to_epicenter_km"] = d["distance_to_epicenter_km"]
    X["elevation_m"] = d["elevation_m"]

    X["depth_missing"] = d["earthquake_depth_km"].isna().astype(int)
    X["elevation_missing"] = d["elevation_m"].isna().astype(int)

    X["magnitude_distance_ratio"] = (
        d["earthquake_magnitude"] /
        (d["distance_to_epicenter_km"] + 1.0)
    )

    X["magnitude_distance_interaction"] = (
        d["earthquake_magnitude"] *
        d["distance_to_epicenter_km"]
    )

    X["depth_distance_ratio"] = (
        d["earthquake_depth_km"] /
        (d["distance_to_epicenter_km"] + 1.0)
    )

    X["log_elevation"] = np.log1p(
        np.maximum(d["elevation_m"], 0)
    )

    # NEW TERRAIN FEATURE
    X["slope_degrees"] = d["slope_degrees"]

    return X


FEATURES = [
    "earthquake_magnitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m",
    "depth_missing",
    "elevation_missing",
    "magnitude_distance_ratio",
    "magnitude_distance_interaction",
    "depth_distance_ratio",
    "log_elevation",
    "slope_degrees"
]


X = make_features(df)
y = df["label"].astype(int)
groups = df["earthquake_id"]

events = list(df["earthquake_id"].unique())

print("=" * 90)
print("P1 LOEO VALIDATION — BASELINE + TERRAIN SLOPE")
print("=" * 90)
print("Events:", len(events))
print("Features:", len(FEATURES))
print()

results = []

for event in events:

    train_mask = groups != event
    test_mask = groups == event

    X_train = X.loc[train_mask, FEATURES]
    X_test = X.loc[test_mask, FEATURES]

    y_train = y.loc[train_mask]
    y_test = y.loc[test_mask]

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=1000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    auc = roc_auc_score(y_test, probabilities)
    f1 = f1_score(y_test, predictions, zero_division=0)
    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )

    event_name = df.loc[test_mask, "earthquake_name"].iloc[0]

    result = {
        "event": event_name,
        "n_cells": int(test_mask.sum()),
        "positive": int(y_test.sum()),
        "negative": int((y_test == 0).sum()),
        "AUC": auc,
        "F1": f1,
        "precision": precision,
        "recall": recall
    }

    results.append(result)

    print(
        f"{event_name}\n"
        f"  AUC={auc:.4f}  "
        f"F1={f1:.4f}  "
        f"Precision={precision:.4f}  "
        f"Recall={recall:.4f}\n"
    )


results_df = pd.DataFrame(results)

print("=" * 90)
print("SUMMARY")
print("=" * 90)

print(results_df.to_string(index=False))

print()
print("Mean:")
print(f"AUC       : {results_df['AUC'].mean():.4f}")
print(f"F1        : {results_df['F1'].mean():.4f}")
print(f"Precision : {results_df['precision'].mean():.4f}")
print(f"Recall    : {results_df['recall'].mean():.4f}")

print()
print("Median:")
print(f"AUC       : {results_df['AUC'].median():.4f}")
print(f"F1        : {results_df['F1'].median():.4f}")
print(f"Precision : {results_df['precision'].median():.4f}")
print(f"Recall    : {results_df['recall'].median():.4f}")

results_df.to_csv(OUTPUT, index=False)

print()
print("Saved:", OUTPUT)
print("=" * 90)