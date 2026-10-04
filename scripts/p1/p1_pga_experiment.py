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

FEATURE_SETS = {
    "slope_only": [
        "slope_degrees",
    ],
    "pga_only": [
        "PGA_g",
    ],
    "slope_pga": [
        "slope_degrees",
        "PGA_g",
    ],
    "slope_pga_distance": [
        "slope_degrees",
        "PGA_g",
        "distance_to_epicenter_km",
    ],
}


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

def run_loeo(df, features):

    events = df[GROUP].dropna().unique()

    results = []

    for event in events:

        train_mask = df[GROUP] != event
        test_mask = df[GROUP] == event

        train_df = df.loc[train_mask]
        test_df = df.loc[test_mask]

        X_train = train_df[features]
        y_train = train_df[TARGET]

        X_test = test_df[features]
        y_test = test_df[TARGET]

        # Safety check
        if y_test.nunique() < 2:
            print(
                f"Skipping {event}: "
                "test set contains only one class."
            )
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

        event_name = test_df[
            "earthquake_name"
        ].iloc[0]

        results.append(
            {
                "earthquake_id": event,
                "earthquake_name": event_name,
                "auc": auc,
                "test_rows": len(test_df),
            }
        )

    return pd.DataFrame(results)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("QUAKESHIELD — PGA EARTHQUAKE-AWARE P1 EXPERIMENT")
    print("=" * 75)

    df = pd.read_csv(DATA_PATH)

    print(f"\nDataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
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
        "distance_to_epicenter_km",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    # --------------------------------------------------------
    # Basic PGA audit
    # --------------------------------------------------------

    print("\nPGA audit:")
    print(
        f"  Missing PGA: "
        f"{df['PGA_g'].isna().sum():,}"
    )

    print(
        f"  PGA min: "
        f"{df['PGA_g'].min():.6f} g"
    )

    print(
        f"  PGA max: "
        f"{df['PGA_g'].max():.6f} g"
    )

    # --------------------------------------------------------
    # Run every feature configuration
    # --------------------------------------------------------

    all_results = []

    for model_name, features in FEATURE_SETS.items():

        print("\n" + "-" * 75)
        print(f"MODEL: {model_name}")
        print(
            "Features: "
            + ", ".join(features)
        )
        print("-" * 75)

        results = run_loeo(
            df,
            features,
        )

        results["model"] = model_name

        all_results.append(results)

        print(
            results[
                [
                    "earthquake_name",
                    "auc",
                    "test_rows",
                ]
            ].to_string(index=False)
        )

        print(
            f"\nMean LOEO AUC: "
            f"{results['auc'].mean():.4f}"
        )

        print(
            f"Std LOEO AUC: "
            f"{results['auc'].std(ddof=0):.4f}"
        )

    # --------------------------------------------------------
    # Combine results
    # --------------------------------------------------------

    combined = pd.concat(
        all_results,
        ignore_index=True,
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = (
        combined
        .groupby("model")
        .agg(
            mean_auc=("auc", "mean"),
            std_auc=("auc", "std"),
            median_auc=("auc", "median"),
            min_auc=("auc", "min"),
            max_auc=("auc", "max"),
        )
        .reset_index()
    )

    print("\n" + "=" * 75)
    print("MODEL SUMMARY")
    print("=" * 75)

    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    # --------------------------------------------------------
    # Baseline comparisons
    # --------------------------------------------------------

    mean_scores = (
        combined
        .groupby("model")["auc"]
        .mean()
    )

    baseline = mean_scores["slope_only"]

    print("\n" + "=" * 75)
    print("COMPARISON WITH SLOPE-ONLY BASELINE")
    print("=" * 75)

    for model_name in FEATURE_SETS:

        score = mean_scores[model_name]
        improvement = score - baseline

        print(
            f"{model_name:25s} "
            f"AUC={score:.4f}  "
            f"Δ={improvement:+.4f}"
        )

    # --------------------------------------------------------
    # Per-event paired comparison
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("PER-EVENT COMPARISON")
    print("=" * 75)

    slope_results = (
        combined[
            combined["model"] == "slope_only"
        ][
            [
                "earthquake_id",
                "earthquake_name",
                "auc",
            ]
        ]
        .rename(
            columns={
                "auc": "slope_only_auc"
            }
        )
    )

    for model_name in [
        "pga_only",
        "slope_pga",
        "slope_pga_distance",
    ]:

        candidate = (
            combined[
                combined["model"] == model_name
            ][
                [
                    "earthquake_id",
                    "auc",
                ]
            ]
            .rename(
                columns={
                    "auc": f"{model_name}_auc"
                }
            )
        )

        comparison = slope_results.merge(
            candidate,
            on="earthquake_id",
        )

        comparison["improvement"] = (
            comparison[f"{model_name}_auc"]
            - comparison["slope_only_auc"]
        )

        print(
            f"\n{model_name} vs slope_only:"
        )

        print(
            comparison[
                [
                    "earthquake_name",
                    "slope_only_auc",
                    f"{model_name}_auc",
                    "improvement",
                ]
            ].to_string(
                index=False,
                float_format=lambda x: f"{x:.4f}",
            )
        )

        print(
            f"Mean improvement: "
            f"{comparison['improvement'].mean():+.4f}"
        )

        print(
            f"Median improvement: "
            f"{comparison['improvement'].median():+.4f}"
        )

        print(
            f"Events improved: "
            f"{(comparison['improvement'] > 0).sum()}/"
            f"{len(comparison)}"
        )

        print(
            f"Events decreased: "
            f"{(comparison['improvement'] < 0).sum()}/"
            f"{len(comparison)}"
        )

    # --------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------

    output_path = (
        "outputs/p1_pga_loeo_results.csv"
    )

    summary_path = (
        "outputs/p1_pga_loeo_summary.csv"
    )

    combined.to_csv(
        output_path,
        index=False,
    )

    summary.to_csv(
        summary_path,
        index=False,
    )

    print("\n" + "=" * 75)
    print("SAVED")
    print("=" * 75)

    print(
        f"Detailed results:\n"
        f"{output_path}"
    )

    print(
        f"\nSummary:\n"
        f"{summary_path}"
    )

    print("\nIMPORTANT:")
    print(
        "These are experimental LOEO results."
    )
    print(
        "The existing slope-only P1 model has NOT been replaced."
    )


if __name__ == "__main__":
    main()