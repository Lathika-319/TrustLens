import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "data/QuakeShield_Final_Dataset_Slope_PGA.csv"

TARGET = "label"
GROUP = "earthquake_id"

FEATURES = [
    "slope_degrees",
    "PGA_g",
]

N_PERMUTATIONS = 100
RANDOM_SEED = 42


# ============================================================
# MODEL
# ============================================================

def build_model():
    return Pipeline(
        [
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
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


# ============================================================
# LOEO
# ============================================================

def run_loeo(df, target_column):
    """
    Leave-one-earthquake-out evaluation.

    Each earthquake is completely held out as the test set.
    """

    events = df[GROUP].dropna().unique()

    aucs = []

    for event in events:

        train_mask = df[GROUP] != event
        test_mask = df[GROUP] == event

        train_df = df.loc[train_mask]
        test_df = df.loc[test_mask]

        X_train = train_df[FEATURES]
        y_train = train_df[target_column]

        X_test = test_df[FEATURES]
        y_test = test_df[target_column]

        # AUC requires both classes in test set
        if y_test.nunique() < 2:
            continue

        model = build_model()

        model.fit(
            X_train,
            y_train,
        )

        y_score = model.predict_proba(
            X_test
        )[:, 1]

        auc = roc_auc_score(
            y_test,
            y_score,
        )

        aucs.append(auc)

    return float(np.mean(aucs))


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("QUAKESHIELD — SLOPE + PGA LOEO PERMUTATION TEST")
    print("=" * 75)

    df = pd.read_csv(DATA_PATH)

    print(f"\nDataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(
        f"Earthquake events: "
        f"{df[GROUP].nunique()}"
    )

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    required = {
        TARGET,
        GROUP,
        "earthquake_name",
        "slope_degrees",
        "PGA_g",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    # --------------------------------------------------------
    # Observed score
    # --------------------------------------------------------

    print("\nCalculating observed LOEO AUC...")

    observed_auc = run_loeo(
        df,
        TARGET,
    )

    print(
        f"Observed mean LOEO AUC: "
        f"{observed_auc:.4f}"
    )

    # --------------------------------------------------------
    # Permutations
    # --------------------------------------------------------

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    permutation_scores = []

    print(
        f"\nRunning {N_PERMUTATIONS} "
        f"within-earthquake permutations..."
    )

    for i in range(N_PERMUTATIONS):

        permuted_df = df.copy()

        # Shuffle labels independently inside
        # each earthquake event.
        for event in permuted_df[GROUP].unique():

            mask = (
                permuted_df[GROUP] == event
            )

            labels = (
                permuted_df.loc[
                    mask,
                    TARGET,
                ]
                .to_numpy()
                .copy()
            )

            rng.shuffle(labels)

            permuted_df.loc[
                mask,
                TARGET,
            ] = labels

        score = run_loeo(
            permuted_df,
            TARGET,
        )

        permutation_scores.append(score)

        print(
            f"Permutation "
            f"{i + 1:3d}/{N_PERMUTATIONS}: "
            f"{score:.4f}"
        )

    permutation_scores = np.asarray(
        permutation_scores,
        dtype=float,
    )

    # --------------------------------------------------------
    # Null distribution statistics
    # --------------------------------------------------------

    null_mean = permutation_scores.mean()
    null_std = permutation_scores.std(
        ddof=1
    )

    null_min = permutation_scores.min()
    null_max = permutation_scores.max()

    p5 = np.percentile(
        permutation_scores,
        5,
    )

    p50 = np.percentile(
        permutation_scores,
        50,
    )

    p95 = np.percentile(
        permutation_scores,
        95,
    )

    # Empirical one-sided permutation p-value.
    #
    # +1 correction avoids zero p-values.
    p_value = (
        np.sum(
            permutation_scores >= observed_auc
        ) + 1
    ) / (
        N_PERMUTATIONS + 1
    )

    count_ge = np.sum(
        permutation_scores >= observed_auc
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("PERMUTATION TEST RESULTS")
    print("=" * 75)

    print(
        f"Observed mean LOEO AUC : "
        f"{observed_auc:.4f}"
    )

    print(
        f"Permutation mean       : "
        f"{null_mean:.4f}"
    )

    print(
        f"Permutation std        : "
        f"{null_std:.4f}"
    )

    print(
        f"Permutation min        : "
        f"{null_min:.4f}"
    )

    print(
        f"Permutation max        : "
        f"{null_max:.4f}"
    )

    print(
        f"5th percentile         : "
        f"{p5:.4f}"
    )

    print(
        f"Median                 : "
        f"{p50:.4f}"
    )

    print(
        f"95th percentile        : "
        f"{p95:.4f}"
    )

    print(
        f"Permutations >= observed: "
        f"{count_ge}/{N_PERMUTATIONS}"
    )

    print(
        f"Empirical one-sided p-value: "
        f"{p_value:.4f}"
    )

    # --------------------------------------------------------
    # Interpretation
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("INTERPRETATION")
    print("=" * 75)

    if observed_auc > p95:

        print(
            "Observed AUC is above the 95th "
            "percentile of the permutation null."
        )

        print(
            "This supports the conclusion that "
            "the slope + PGA model contains signal "
            "beyond the within-earthquake shuffled null."
        )

    else:

        print(
            "Observed AUC is NOT above the 95th "
            "percentile of the permutation null."
        )

        print(
            "The observed performance is not clearly "
            "separated from the permutation null."
        )

    print(
        "\nIMPORTANT:"
    )

    print(
        "This is a diagnostic permutation test, "
        "not definitive statistical proof."
    )

    print(
        "Only 100 permutations are used, so the "
        "smallest possible corrected empirical "
        "p-value is 1/(100+1) ≈ 0.0099."
    )

    print(
        "This test does not prove that PGA itself "
        "causes the improvement or that the model "
        "will generalize to future earthquakes."
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    output_path = (
        "outputs/p1_loeo_slope_pga_permutation.csv"
    )

    summary = pd.DataFrame(
        {
            "observed_auc": [
                observed_auc
            ],
            "permutation_mean": [
                null_mean
            ],
            "permutation_std": [
                null_std
            ],
            "permutation_min": [
                null_min
            ],
            "permutation_max": [
                null_max
            ],
            "p5": [
                p5
            ],
            "median": [
                p50
            ],
            "p95": [
                p95
            ],
            "permutations_ge_observed": [
                count_ge
            ],
            "n_permutations": [
                N_PERMUTATIONS
            ],
            "empirical_p_value": [
                p_value
            ],
        }
    )

    summary.to_csv(
        output_path,
        index=False,
    )

    print("\n" + "=" * 75)
    print("SAVED")
    print("=" * 75)

    print(
        f"Results saved to:\n"
        f"{output_path}"
    )

    print(
        "\nExisting slope-only P1 model remains unchanged."
    )


if __name__ == "__main__":
    main()