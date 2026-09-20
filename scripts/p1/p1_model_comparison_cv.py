import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

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
# Feature engineering
# -----------------------------

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

df["magnitude_distance_ratio"] = magnitude / (distance + 1)
df["magnitude_distance_interaction"] = magnitude * distance
df["depth_distance_ratio"] = depth / (distance + 1)
df["log_elevation"] = np.log1p(elevation)

# -----------------------------
# Clean feature set
# No coordinates
# -----------------------------

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
groups = df["earthquake_id"]

# -----------------------------
# Models
# -----------------------------

models = {

    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=1000,
            random_state=42
        ))
    ]),

    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        ))
    ]),

    "Gradient Boosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", GradientBoostingClassifier(
            random_state=42
        ))
    ])
}

# -----------------------------
# 5-Fold Group CV
# -----------------------------

gkf = GroupKFold(n_splits=5)

all_results = {}

for model_name, model in models.items():

    scores = {
        "accuracy": [],
        "precision": [],
        "recall": [],
        "f1": [],
        "roc_auc": []
    }

    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    for fold, (train_idx, test_idx) in enumerate(
        gkf.split(X, y, groups), start=1
    ):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        scores["accuracy"].append(
            accuracy_score(y_test, y_pred)
        )

        scores["precision"].append(
            precision_score(
                y_test, y_pred, zero_division=0
            )
        )

        scores["recall"].append(
            recall_score(
                y_test, y_pred, zero_division=0
            )
        )

        scores["f1"].append(
            f1_score(
                y_test, y_pred, zero_division=0
            )
        )

        scores["roc_auc"].append(
            roc_auc_score(y_test, y_prob)
        )

        print(
            f"Fold {fold}: "
            f"Accuracy={scores['accuracy'][-1]:.4f}, "
            f"Recall={scores['recall'][-1]:.4f}, "
            f"F1={scores['f1'][-1]:.4f}, "
            f"ROC-AUC={scores['roc_auc'][-1]:.4f}"
        )

    all_results[model_name] = scores

# -----------------------------
# Final comparison
# -----------------------------

print("\n" + "=" * 70)
print("FINAL 5-FOLD GROUP CV MODEL COMPARISON")
print("=" * 70)

for model_name, scores in all_results.items():

    print(f"\n{model_name}")

    for metric, values in scores.items():

        print(
            f"{metric.upper():10s}: "
            f"{np.mean(values):.4f} +/- "
            f"{np.std(values):.4f}"
        )
