import os
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


DATA_FILE = r"outputs\p4_lateral_spreading_clean_dataset.csv"
OUTPUT_FILE = r"outputs\p4_loeo_permutation_results.csv"

N_PERMUTATIONS = 100
RANDOM_SEED = 42

FEATURES = [
    "PGA_g",
    "PGV_mps",
    "Arias_Intensity",
]

TARGET = "lateral_spreading"
GROUP = "EVNT_ID"


# ============================================================
# MODEL
# ============================================================

def make_model():
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


# ============================================================
# LOEO FUNCTION
# ============================================================

def loeo_auc(df, target_values):

    events = sorted(
        df[GROUP].dropna().unique()
    )

    all_true = []
    all_score = []

    for event_id in events:

        train_mask = (
            df[GROUP] != event_id
        )

        test_mask = (
            df[GROUP] == event_id
        )

        X_train = df.loc[
            train_mask,
            FEATURES
        ]

        X_test = df.loc[
            test_mask,
            FEATURES
        ]

        y_train = target_values[
            train_mask.to_numpy()
        ]

        y_test = target_values[
            test_mask.to_numpy()
        ]

        # Training fold must contain both classes.
        if len(np.unique(y_train)) < 2:
            continue

        model = make_model()

        model.fit(
            X_train,
            y_train,
        )

        scores = model.predict_proba(
            X_test
        )[:, 1]

        all_true.extend(
            y_test.tolist()
        )

        all_score.extend(
            scores.tolist()
        )

    all_true = np.asarray(
        all_true
    )

    all_score = np.asarray(
        all_score
    )

    return roc_auc_score(
        all_true,
        all_score,
    )


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("QUAKESHIELD — P4 LOEO PERMUTATION DIAGNOSTIC")
print("=" * 70)

df = pd.read_csv(DATA_FILE)

print(
    f"\nDataset rows: {len(df)}"
)

print(
    f"Events: {df[GROUP].nunique()}"
)

print(
    f"Observed positive: "
    f"{df[TARGET].sum()}"
)

print(
    f"Observed negative: "
    f"{(df[TARGET] == 0).sum()}"
)


# ============================================================
# OBSERVED AUC
# ============================================================

y_observed = (
    df[TARGET]
    .astype(int)
    .to_numpy()
)

print("\nCalculating observed LOEO AUC...")

observed_auc = loeo_auc(
    df,
    y_observed,
)

print(
    f"Observed LOEO ROC-AUC: "
    f"{observed_auc:.4f}"
)


# ============================================================
# PERMUTATION TEST
# ============================================================

print("\n" + "=" * 70)
print("WITHIN-EARTHQUAKE PERMUTATION")
print("=" * 70)

rng = np.random.default_rng(
    RANDOM_SEED
)

events = sorted(
    df[GROUP].unique()
)

# We shuffle labels ONLY within each earthquake.
# This preserves the event-level class balance.

permutation_aucs = []

for i in range(
    N_PERMUTATIONS
):

    permuted_y = y_observed.copy()

    for event_id in events:

        idx = np.flatnonzero(
            df[GROUP].to_numpy()
            == event_id
        )

        if len(idx) > 1:

            permuted_y[idx] = rng.permutation(
                permuted_y[idx]
            )

    auc = loeo_auc(
        df,
        permuted_y,
    )

    permutation_aucs.append(
        auc
    )

    print(
        f"Permutation "
        f"{i + 1:3d}/{N_PERMUTATIONS}: "
        f"{auc:.4f}"
    )


# ============================================================
# SUMMARY
# ============================================================

permutation_aucs = np.asarray(
    permutation_aucs
)

null_mean = (
    permutation_aucs.mean()
)

null_std = (
    permutation_aucs.std(
        ddof=1
    )
)

null_min = (
    permutation_aucs.min()
)

null_max = (
    permutation_aucs.max()
)

null_p5 = np.percentile(
    permutation_aucs,
    5,
)

null_median = np.percentile(
    permutation_aucs,
    50,
)

null_p95 = np.percentile(
    permutation_aucs,
    95,
)

count_ge_observed = (
    permutation_aucs
    >= observed_auc
).sum()

empirical_p = (
    count_ge_observed + 1
) / (
    N_PERMUTATIONS + 1
)


# ============================================================
# SAVE
# ============================================================

summary = pd.DataFrame(
    {
        "observed_auc": [observed_auc],
        "permutation_mean": [null_mean],
        "permutation_std": [null_std],
        "permutation_min": [null_min],
        "permutation_max": [null_max],
        "permutation_p5": [null_p5],
        "permutation_median": [null_median],
        "permutation_p95": [null_p95],
        "permutations_ge_observed": [
            count_ge_observed
        ],
        "empirical_p": [empirical_p],
        "n_permutations": [
            N_PERMUTATIONS
        ],
    }
)

summary.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("P4 PERMUTATION SUMMARY")
print("=" * 70)

print(
    f"Observed LOEO AUC : "
    f"{observed_auc:.4f}"
)

print(
    f"Null mean         : "
    f"{null_mean:.4f}"
)

print(
    f"Null SD           : "
    f"{null_std:.4f}"
)

print(
    f"Null min          : "
    f"{null_min:.4f}"
)

print(
    f"Null max          : "
    f"{null_max:.4f}"
)

print(
    f"Null 5th pct      : "
    f"{null_p5:.4f}"
)

print(
    f"Null median       : "
    f"{null_median:.4f}"
)

print(
    f"Null 95th pct     : "
    f"{null_p95:.4f}"
)

print(
    f"Permutations >= observed: "
    f"{count_ge_observed}/{N_PERMUTATIONS}"
)

print(
    f"Empirical p-value : "
    f"{empirical_p:.4f}"
)

print(
    f"\nSaved: {OUTPUT_FILE}"
)


# ============================================================
# INTERPRETATION
# ============================================================

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if empirical_p < 0.05:

    print(
        "Observed AUC is unusually high relative "
        "to the within-earthquake permutation null."
    )

    print(
        "RESULT: diagnostic signal detected."
    )

    print(
        "NEXT: perform feature-ablation and "
        "stability diagnostics before promotion."
    )

else:

    print(
        "Observed AUC is not clearly separated "
        "from the within-earthquake permutation null."
    )

    print(
        "RESULT: insufficient evidence for "
        "reliable P4 predictive signal."
    )

    print(
        "RECOMMENDATION: do NOT promote P4."
    )

print(
    "\nIMPORTANT: permutation significance does "
    "not prove physical causality or future generalization."
)