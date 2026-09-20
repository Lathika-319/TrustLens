import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

print("Dataset loaded successfully!")
print("Original shape:", df.shape)


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

# Missing-value indicators
df["depth_missing"] = df["earthquake_depth_km"].isna().astype(int)
df["elevation_missing"] = df["elevation_m"].isna().astype(int)

# Safe versions for calculations
depth = df["earthquake_depth_km"].fillna(
    df["earthquake_depth_km"].median()
)

elevation = df["elevation_m"].fillna(
    df["elevation_m"].median()
)

magnitude = df["earthquake_magnitude"]
distance = df["distance_to_epicenter_km"]


# ------------------------------------------------------------
# Magnitude-distance interaction
# ------------------------------------------------------------

# Higher magnitude and shorter distance generally indicate
# stronger earthquake influence at the location.
df["magnitude_distance_ratio"] = magnitude / (distance + 1.0)

# Interaction between magnitude and distance
df["magnitude_distance_interaction"] = (
    magnitude * distance
)


# ------------------------------------------------------------
# Depth-related feature
# ------------------------------------------------------------

# Earthquake depth relative to epicentral distance
df["depth_distance_ratio"] = (
    depth / (distance + 1.0)
)


# ------------------------------------------------------------
# Elevation-related feature
# ------------------------------------------------------------

# Log transformation reduces the effect of very large
# elevation values while retaining elevation information.
df["log_elevation"] = np.log1p(elevation)


# ============================================================
# 3. SELECT P1 FEATURES
# ============================================================

features = [
    "earthquake_magnitude",
    "earthquake_latitude",
    "earthquake_longitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m",

    # Engineered features
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


print("\nP1 FEATURES")
print("=" * 70)

for feature in features:
    print(feature)


# ============================================================
# 4. GROUP-AWARE TRAIN / TEST SPLIT
# ============================================================

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

groups_train = groups.iloc[train_idx]
groups_test = groups.iloc[test_idx]


print("\nTRAIN / TEST SPLIT")
print("=" * 70)

print("Training rows:", len(X_train))
print("Testing rows :", len(X_test))

print("\nTraining earthquakes:")
print(groups_train.unique())

print("\nTesting earthquakes:")
print(groups_test.unique())


# ============================================================
# 5. GRADIENT BOOSTING MODEL
# ============================================================

model = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "model",
        GradientBoostingClassifier(
            random_state=42
        )
    )
])


# ============================================================
# 6. TRAIN MODEL
# ============================================================

print("\nTRAINING P1 MODEL...")
print("=" * 70)

model.fit(X_train, y_train)


# ============================================================
# 7. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)

y_prob = model.predict_proba(X_test)[:, 1]


# ============================================================
# 8. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

auc = roc_auc_score(
    y_test,
    y_prob
)

cm = confusion_matrix(
    y_test,
    y_pred
)


print("\nP1 FEATURE-ENGINEERED RESULTS")
print("=" * 70)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {auc:.4f}")

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 9. INTERPRETATION OF CONFUSION MATRIX
# ============================================================

tn, fp, fn, tp = cm.ravel()

print("\nCONFUSION MATRIX DETAILS")
print("=" * 70)

print("True Negatives :", tn)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Positives :", tp)


print("\nP1 FEATURE ENGINEERING COMPLETE")
