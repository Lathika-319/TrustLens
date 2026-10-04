import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

DATA = r"TrustLens-push\data\QuakeShield_Final_Dataset.csv"

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
]

df = pd.read_csv(DATA)

# Recreate exactly the same engineered features
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

X = df[FEATURES]
y = df["label"].copy()
groups = df["earthquake_id"]

model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

N_PERMUTATIONS = 100
rng = np.random.default_rng(42)

cv = GroupKFold(n_splits=5)

scores = []

for permutation in range(N_PERMUTATIONS):

    y_perm = y.copy()

    # Shuffle labels WITHIN each earthquake.
    # This preserves each event's class balance.
    for event_id in groups.unique():
        idx = np.where(groups.values == event_id)[0]
        y_perm.iloc[idx] = rng.permutation(y.iloc[idx].values)

    fold_scores = []

    for train_idx, test_idx in cv.split(X, y_perm, groups):

        model.fit(
            X.iloc[train_idx],
            y_perm.iloc[train_idx]
        )

        probabilities = model.predict_proba(
            X.iloc[test_idx]
        )[:, 1]

        auc = roc_auc_score(
            y_perm.iloc[test_idx],
            probabilities
        )

        fold_scores.append(auc)

    scores.append(np.mean(fold_scores))

scores = np.array(scores)

print("=" * 70)
print("P1 LABEL-PERMUTATION BASELINE")
print("=" * 70)

print(f"Permutations : {N_PERMUTATIONS}")
print(f"Mean AUC     : {scores.mean():.4f}")
print(f"Std AUC      : {scores.std():.4f}")
print(f"Min AUC      : {scores.min():.4f}")
print(f"Max AUC      : {scores.max():.4f}")
print(f"P5           : {np.percentile(scores, 5):.4f}")
print(f"P50          : {np.percentile(scores, 50):.4f}")
print(f"P95          : {np.percentile(scores, 95):.4f}")

REAL_AUC = 0.5682

print()
print(f"Observed real AUC : {REAL_AUC:.4f}")
print(
    f"Permutation mean  : {scores.mean():.4f}"
)

print()
print(
    "Fraction of permutations >= observed:",
    round(np.mean(scores >= REAL_AUC), 4)
)

print("=" * 70)