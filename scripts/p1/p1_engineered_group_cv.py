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

# Load dataset
df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

# -----------------------------
# Feature Engineering
# -----------------------------

# Missing indicators
df["depth_missing"] = df["earthquake_depth_km"].isna().astype(int)
df["elevation_missing"] = df["elevation_m"].isna().astype(int)

# Fill missing values temporarily for feature engineering
depth = df["earthquake_depth_km"].fillna(
    df["earthquake_depth_km"].median()
)

elevation = df["elevation_m"].fillna(
    df["elevation_m"].median()
)

distance = df["distance_to_epicenter_km"]

magnitude = df["earthquake_magnitude"]

# Engineered features
df["magnitude_distance_ratio"] = magnitude / (distance + 1)

df["magnitude_distance_interaction"] = magnitude * distance

df["depth_distance_ratio"] = depth / (distance + 1)

df["log_elevation"] = np.log1p(elevation)

# -----------------------------
# Features and target
# -----------------------------

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

# -----------------------------
# 5-Fold Group Cross Validation
# -----------------------------

gkf = GroupKFold(n_splits=5)

metrics = {
    "accuracy": [],
    "precision": [],
    "recall": [],
    "f1": [],
    "roc_auc": []
}

fold = 1

for train_idx, test_idx in gkf.split(X, y, groups):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", GradientBoostingClassifier(
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)

    metrics["accuracy"].append(acc)
    metrics["precision"].append(prec)
    metrics["recall"].append(rec)
    metrics["f1"].append(f1)
    metrics["roc_auc"].append(auc)

    print(f"\nFold {fold}")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")

    fold += 1

# -----------------------------
# Final Results
# -----------------------------

print("\n" + "=" * 45)
print("5-FOLD GROUP CROSS-VALIDATION RESULTS")
print("=" * 45)

for metric, values in metrics.items():
    print(
        f"{metric.upper():10s}: "
        f"{np.mean(values):.4f} +/- {np.std(values):.4f}"
    )
