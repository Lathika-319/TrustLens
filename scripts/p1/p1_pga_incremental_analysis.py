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

BASE_FEATURES = [
    "slope_degrees",
]

PGA_FEATURES = [
    "slope_degrees",
    "PGA_g",
]


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
# SAME-FOLD LOEO COMPARISON
# ============================================================

def evaluate_event(
    train_df,
    test_df,
    features,
):
    """
    Train on all other earthquakes and evaluate
    the held-out earthquake.
    """

    X_train = train_df[features]
    y_train = train_df[TARGET]

    X_test = test_df[features]
    y_test = test_df[TARGET]

    model = build_model()

    model.fit(
        X_train,
        y_train,
    )

    y_score = model.predict_proba(
        X_test
    )[:, 1]

    return roc_auc_score(
        y_test,
        y_score,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("QUAKESHIELD — INCREMENTAL PGA ANALYSIS")
    print("=" * 75)

    df = pd.read_csv(DATA_PATH)

    print(f"\nDataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(
        f"Earthquake events: "
        f"{df[GROUP].nunique()}"
    )

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

    events = (
        df[GROUP]
        .dropna()
        .unique()
    )

    results = []

    # ========================================================
    # EVENT-BY-EVENT PAIRED TEST
    # ========================================================

    for event in events:

        train_mask = df[GROUP] != event
        test_mask = df[GROUP] == event

        train_df = df.loc[train_mask]
        test_df = df.loc[test_mask]

        event_name = test_df[
            "earthquake_name"
        ].iloc[0]

        # ----------------------------------------------------
        # Same held-out event for both models
        # ----------------------------------------------------

        slope_auc = evaluate_event(
            train_df,
            test_df,
            BASE_FEATURES,
        )

        slope_pga_auc = evaluate_event(
            train_df,
            test_df,
            PGA_FEATURES,
        )

        improvement = (
            slope_pga_auc - slope_auc
        )

        results.append(
            {
                "earthquake_id": event,
                "earthquake_name": event_name,
                "slope_only_auc": slope_auc,
                "slope_pga_auc": slope_pga_auc,
                "improvement": improvement,
                "test_rows": len(test_df),
            }
        )

    results_df = pd.DataFrame(results)

    # ========================================================
    # EVENT RESULTS
    # ========================================================

    print("\n" + "=" * 75)
    print("EVENT-BY-EVENT RESULTS")
    print("=" * 75)

    print(
        results_df[
            [
                "earthquake_name",
                "slope_only_auc",
                "slope_pga_auc",
                "improvement",
                "test_rows",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    improvements = results_df[
        "improvement"
    ]

    print("\n" + "=" * 75)
    print("INCREMENTAL PGA SUMMARY")
    print("=" * 75)

    print(
        f"Mean slope-only AUC: "
        f"{results_df['slope_only_auc'].mean():.4f}"
    )

    print(
        f"Mean slope + PGA AUC: "
        f"{results_df['slope_pga_auc'].mean():.4f}"
    )

    print(
        f"Mean improvement: "
        f"{improvements.mean():+.4f}"
    )

    print(
        f"Median improvement: "
        f"{improvements.median():+.4f}"
    )

    print(
        f"Std improvement: "
        f"{improvements.std(ddof=1):.4f}"
    )

    print(
        f"Minimum improvement: "
        f"{improvements.min():+.4f}"
    )

    print(
        f"Maximum improvement: "
        f"{improvements.max():+.4f}"
    )

    print(
        f"Events improved: "
        f"{(improvements > 0).sum()}/"
        f"{len(improvements)}"
    )

    print(
        f"Events unchanged: "
        f"{(improvements == 0).sum()}/"
        f"{len(improvements)}"
    )

    print(
        f"Events decreased: "
        f"{(improvements < 0).sum()}/"
        f"{len(improvements)}"
    )

    # ========================================================
    # ROBUSTNESS COUNTS
    # ========================================================

    print("\n" + "=" * 75)
    print("ROBUSTNESS CHECK")
    print("=" * 75)

    thresholds = [
        0.00,
        0.01,
        0.02,
        0.05,
        0.10,
    ]

    for threshold in thresholds:

        count = (
            improvements >= threshold
        ).sum()

        print(
            f"Events with improvement >= "
            f"{threshold:.2f}: "
            f"{count}/{len(improvements)}"
        )

    # ========================================================
    # LARGE NEGATIVE CHANGES
    # ========================================================

    print("\n" + "=" * 75)
    print("LARGEST EVENT-LEVEL CHANGES")
    print("=" * 75)

    largest_improvements = (
        results_df
        .sort_values(
            "improvement",
            ascending=False,
        )
        .head(3)
    )

    largest_decreases = (
        results_df
        .sort_values(
            "improvement",
            ascending=True,
        )
        .head(3)
    )

    print("\nLargest improvements:")

    print(
        largest_improvements[
            [
                "earthquake_name",
                "improvement",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:+.4f}",
        )
    )

    print("\nLargest decreases:")

    print(
        largest_decreases[
            [
                "earthquake_name",
                "improvement",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:+.4f}",
        )
    )

    # ========================================================
    # INTERPRETATION
    # ========================================================

    print("\n" + "=" * 75)
    print("INTERPRETATION")
    print("=" * 75)

    improved = (
        improvements > 0
    ).sum()

    decreased = (
        improvements < 0
    ).sum()

    if (
        improvements.mean() > 0
        and improved > decreased
    ):
        print(
            "PGA provides a positive incremental "
            "contribution over slope-only performance "
            "in this LOEO experiment."
        )
    else:
        print(
            "PGA does not show a consistently positive "
            "incremental contribution over slope-only "
            "performance in this LOEO experiment."
        )

    print(
        "\nThis analysis uses the same held-out "
        "earthquake for both models."
    )

    print(
        "Therefore the event-level differences are "
        "paired comparisons."
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "The dataset contains only 9 earthquake events."
    )

    print(
        "Therefore these results support PGA as an "
        "experimental candidate, but do not establish "
        "generalization to future earthquakes."
    )

    print(
        "The existing production slope-only model "
        "has NOT been replaced."
    )

    # ========================================================
    # SAVE
    # ========================================================

    output_path = (
        "outputs/p1_pga_incremental_analysis.csv"
    )

    results_df.to_csv(
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


if __name__ == "__main__":
    main()