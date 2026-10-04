import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

DATA = r"TrustLens-push\data\QuakeShield_Final_Dataset_Slope.csv"
OUTPUT = r"TrustLens-push\outputs\p1_loeo_slope_permutation.csv"

N_PERMUTATIONS = 100
RANDOM_SEED = 42

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

rng = np.random.RandomState(RANDOM_SEED)


def run_loeo(y_values):

    aucs = []

    for event in events:

        train_mask = groups != event
        test_mask = groups == event

        X_train = X.loc[train_mask, FEATURES]
        X_test = X.loc[test_mask, FEATURES]

        y_train = y_values.loc[train_mask]
        y_test = y_values.loc[test_mask]

        # Skip pathological test folds if permutation creates one class.
        if y_test.nunique() < 2 or y_train.nunique() < 2:
            continue

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

        auc = roc_auc_score(y_test, probabilities)
        aucs.append(auc)

    if len(aucs) != len(events):
        return np.nan

    return np.mean(aucs)


print("=" * 90)
print("MATCHED LOEO LABEL-PERMUTATION TEST")
print("=" * 90)
print("Features:", len(FEATURES))
print("Events:", len(events))
print("Permutations:", N_PERMUTATIONS)
print("Seed:", RANDOM_SEED)
print()

# -------------------------------------------------------------------
# REAL LABEL RESULT
# -------------------------------------------------------------------

observed_auc = run_loeo(y)

print(f"Observed LOEO mean AUC: {observed_auc:.4f}")
print()

# -------------------------------------------------------------------
# PERMUTATIONS
# -------------------------------------------------------------------

permutation_results = []

for i in range(N_PERMUTATIONS):

    shuffled = y.copy()

    # Shuffle labels WITHIN each earthquake event.
    shuffled_values = shuffled.to_numpy().copy()

    for event in events:

        idx = np.where(groups.to_numpy() == event)[0]

        shuffled_values[idx] = rng.permutation(
            shuffled_values[idx]
        )

    shuffled_series = pd.Series(
        shuffled_values,
        index=y.index
    )

    auc = run_loeo(shuffled_series)

    permutation_results.append({
        "permutation": i + 1,
        "mean_loeo_auc": auc
    })

    if (i + 1) % 10 == 0:
        print(
            f"Completed {i + 1}/{N_PERMUTATIONS}"
        )


perm_df = pd.DataFrame(permutation_results)

valid = perm_df["mean_loeo_auc"].dropna()

print()
print("=" * 90)
print("RESULTS")
print("=" * 90)

print(f"Observed AUC : {observed_auc:.4f}")
print(f"Perm mean    : {valid.mean():.4f}")
print(f"Perm std     : {valid.std():.4f}")
print(f"Perm min     : {valid.min():.4f}")
print(f"Perm max     : {valid.max():.4f}")

print()
print(f"P5           : {valid.quantile(0.05):.4f}")
print(f"P50          : {valid.quantile(0.50):.4f}")
print(f"P95          : {valid.quantile(0.95):.4f}")

count_ge = (valid >= observed_auc).sum()

# Add +1 correction so the empirical p-value cannot be exactly zero.
empirical_p = (count_ge + 1) / (len(valid) + 1)

print()
print(
    "Permutations >= observed:",
    count_ge,
    "/",
    len(valid)
)

print(
    f"Empirical one-sided p-value: {empirical_p:.4f}"
)

print()
print("=" * 90)

perm_df.to_csv(OUTPUT, index=False)

print("Saved:", OUTPUT)
print("=" * 90)