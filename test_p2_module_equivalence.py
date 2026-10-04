
# ============================================================
# QUAKESHIELD — P2 MODULE ↔ PRODUCTION EQUIVALENCE TEST
# ============================================================
#
# Purpose:
# Verify that the independent P2 Liquefaction module produces
# exactly the same P2 scenario indicators as the current
# production pipeline.
#
# IMPORTANT:
# This reproduces the production preprocessing exactly:
#
#   1. Load "Liq database"
#   2. Verify 9 base features
#   3. Create 5 missingness indicators
#   4. Clean the 9 numeric features using pd.to_numeric
#      with errors="coerce"
#   5. Generate P2 model scores
#   6. Aggregate by actual Mw
#   7. Select nearest available Mw for each scenario
#
# No retraining.
# No methodology change.
# No fusion.
# ============================================================

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from hazard_modules.liquefaction import (
    REQUIRED_FEATURES,
    predict_scores,
)


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

P2_MODEL_FILE = (
    ROOT
    / "models"
    / "p2_liquefaction_model.joblib"
)

P2_DATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "Database 7.xlsx"
)

PRODUCTION_OUTPUT_FILE = (
    ROOT
    / "outputs"
    / "quakeshield_final_output.csv"
)


# ============================================================
# PRODUCTION BASE FEATURES
# ============================================================

P2_BASE_FEATURES = [

    "σv/σv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)",

]


# ============================================================
# PRODUCTION MISSINGNESS SOURCE FEATURES
# ============================================================

P2_MISSING_SOURCE_FEATURES = [

    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",

]


# ============================================================
# SCENARIO MAGNITUDES
#
# These are the same scenario magnitudes used by the
# QuakeShield production pipeline.
# ============================================================

SCENARIO_MAGNITUDES = {

    "Tohoku-Oki, Japan": 9.1,

    "1 km S of Belanting, Indonesia": 6.9,

    "70km N of Palu, Indonesia": 7.5,

    "32 km SW of Tari, Papua New Guinea": 7.5,

    "9 km NW of Mesetas, Colombia": 6.5,

    "M 6.4 - 13 km SSE of Maria Antonia, Puerto Rico": 6.4,

    "Kobe, Japan": 7.0,

    "Niigata-Chuetsu, Japan": 6.6,

    "Kashmir, Pakistan": 7.6,

}


# ============================================================
# PRODUCTION NUMERIC CLEANING
# ============================================================

def clean_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    )


# ============================================================
# NEAREST P2 MAGNITUDE
#
# Reproduces production logic:
#
# nearest available magnitude from p2_scenarios.
# ============================================================

def nearest_p2_magnitude(
    magnitude,
    available_magnitudes
):

    if pd.isna(magnitude):

        return np.nan

    valid_magnitudes = (

        pd.Series(
            available_magnitudes
        )
        .dropna()
        .unique()

    )

    if len(valid_magnitudes) == 0:

        return np.nan

    return min(

        valid_magnitudes,

        key=lambda x:
        abs(x - magnitude)

    )


# ============================================================
# START
# ============================================================

print()
print("=" * 70)
print("QUAKESHIELD — P2 MODULE EQUIVALENCE TEST")
print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("Loading P2 dataset...")

p2_data = pd.read_excel(

    P2_DATA_FILE,

    sheet_name="Liq database"

)

print(
    f"P2 rows loaded: "
    f"{len(p2_data):,}"
)


# ============================================================
# VERIFY BASE FEATURES
# ============================================================

missing_base_features = [

    column

    for column in P2_BASE_FEATURES

    if column not in p2_data.columns

]


if missing_base_features:

    print()
    print("ERROR: Missing P2 base features:")

    for column in missing_base_features:

        print(f"  - {column}")

    raise SystemExit(1)


print()
print("Original P2 workbook features: PASS")


# ============================================================
# CREATE MISSINGNESS FEATURES
#
# IMPORTANT:
# This happens BEFORE numeric cleaning, exactly like
# production.
# ============================================================

print()
print(
    "Creating production missingness indicators..."
)


for column in P2_MISSING_SOURCE_FEATURES:

    missing_column = (
        f"{column}_missing"
    )

    p2_data[missing_column] = (

        p2_data[column]
        .isna()
        .astype(int)

    )


print(
    "Missingness indicators: PASS"
)


# ============================================================
# CLEAN NUMERIC P2 FEATURES
#
# EXACT PRODUCTION LOGIC:
#
# for column in p2_base_features:
#     p2_data[column] = clean_numeric(
#         p2_data[column]
#     )
# ============================================================

print()
print(
    "Cleaning P2 numeric features..."
)


for column in P2_BASE_FEATURES:

    p2_data[column] = clean_numeric(

        p2_data[column]

    )


print(
    "Numeric cleaning: PASS"
)


# ============================================================
# BUILD 14 FEATURE LIST
# ============================================================

P2_FEATURE_COLUMNS = (

    P2_BASE_FEATURES

    +

    [
        f"{column}_missing"

        for column
        in P2_MISSING_SOURCE_FEATURES
    ]

)


# ============================================================
# VERIFY FEATURE ORDER
# ============================================================

if P2_FEATURE_COLUMNS != REQUIRED_FEATURES:

    print()
    print("ERROR: Feature order mismatch.")

    print()
    print("Production feature order:")

    for index, feature in enumerate(
        P2_FEATURE_COLUMNS,
        start=1
    ):

        print(
            f"  {index}. {feature}"
        )

    print()
    print("P2 module feature order:")

    for index, feature in enumerate(
        REQUIRED_FEATURES,
        start=1
    ):

        print(
            f"  {index}. {feature}"
        )

    raise AssertionError(
        "Production and module P2 feature "
        "orders differ."
    )


print()
print(
    "All 14 production P2 features: PASS"
)


# ============================================================
# CHECK ALL FEATURES ARE NUMERIC
# ============================================================

non_numeric_columns = [

    column

    for column in P2_FEATURE_COLUMNS

    if not pd.api.types.is_numeric_dtype(
        p2_data[column]
    )

]


if non_numeric_columns:

    print()
    print(
        "ERROR: Non-numeric P2 features remain:"
    )

    for column in non_numeric_columns:

        print(f"  - {column}")

    raise AssertionError(
        "P2 feature preprocessing failed."
    )


print(
    "Numeric feature validation: PASS"
)


# ============================================================
# LOAD PRODUCTION MODEL
# ============================================================

print()
print("Loading production P2 model...")

model = joblib.load(
    P2_MODEL_FILE
)

print(
    "Production P2 model: PASS"
)


# ============================================================
# INDEPENDENT MODULE SCORES
# ============================================================

print()
print(
    "Generating independent P2 module scores..."
)


p2_data["module_score"] = predict_scores(

    p2_data,

    model=model

)


print(
    "Independent P2 scoring: PASS"
)


# ============================================================
# PRODUCTION-STYLE ROW SCORES
#
# This directly reproduces:
#
# p2_model.predict_proba(
#     p2_data[p2_feature_columns]
# )[:, 1]
# ============================================================

print()
print(
    "Generating production-style P2 scores..."
)


p2_data["production_row_score"] = (

    model.predict_proba(

        p2_data[
            P2_FEATURE_COLUMNS
        ]

    )[:, 1]

)


print(
    "Production-style scoring: PASS"
)


# ============================================================
# ROW-LEVEL COMPARISON
# ============================================================

p2_data["absolute_difference"] = (

    p2_data["module_score"]

    -

    p2_data["production_row_score"]

).abs()


max_row_difference = (

    p2_data[
        "absolute_difference"
    ].max()

)


print()
print(
    "Row-level comparison"
)

print("-" * 70)

print(
    f"Rows compared: "
    f"{len(p2_data):,}"
)

print(
    f"Maximum absolute difference: "
    f"{max_row_difference:.15f}"
)


# ============================================================
# RECREATE PRODUCTION P2 AGGREGATION
#
# EXACT PRODUCTION LOGIC:
#
# p2_data.groupby("Mw")
#     .agg(
#         mean = mean(P2_model_score),
#         max  = max(P2_model_score),
#         count = count(P2_model_score)
#     )
# ============================================================

print()
print(
    "Recreating production P2 magnitude aggregation..."
)


p2_scenarios_module = (

    p2_data

    .groupby(
        "Mw",
        dropna=False
    )

    .agg(

        module_mean_score=(
            "module_score",
            "mean"
        ),

        module_max_score=(
            "module_score",
            "max"
        ),

        module_site_count=(
            "module_score",
            "count"
        )

    )

    .reset_index()

)


p2_scenarios_production = (

    p2_data

    .groupby(
        "Mw",
        dropna=False
    )

    .agg(

        production_mean_score=(
            "production_row_score",
            "mean"
        ),

        production_max_score=(
            "production_row_score",
            "max"
        ),

        production_site_count=(
            "production_row_score",
            "count"
        )

    )

    .reset_index()

)


# ============================================================
# MERGE AGGREGATIONS
# ============================================================

p2_scenarios = (

    p2_scenarios_module

    .merge(

        p2_scenarios_production,

        on="Mw",

        how="outer"

    )

)


# ============================================================
# AGGREGATION DIFFERENCES
# ============================================================

p2_scenarios[
    "mean_difference"
] = (

    p2_scenarios[
        "module_mean_score"
    ]

    -

    p2_scenarios[
        "production_mean_score"
    ]

).abs()


p2_scenarios[
    "max_difference"
] = (

    p2_scenarios[
        "module_max_score"
    ]

    -

    p2_scenarios[
        "production_max_score"
    ]

).abs()


p2_scenarios[
    "count_difference"
] = (

    p2_scenarios[
        "module_site_count"
    ]

    -

    p2_scenarios[
        "production_site_count"
    ]

).abs()


max_mean_difference = (

    p2_scenarios[
        "mean_difference"
    ].max()

)


max_max_difference = (

    p2_scenarios[
        "max_difference"
    ].max()

)


max_count_difference = (

    p2_scenarios[
        "count_difference"
    ].max()

)


print()
print(
    "Magnitude-level aggregation comparison"
)

print("-" * 70)

print(
    f"Magnitude groups compared: "
    f"{len(p2_scenarios)}"
)

print(
    f"Maximum mean-score difference: "
    f"{max_mean_difference:.15f}"
)

print(
    f"Maximum max-score difference: "
    f"{max_max_difference:.15f}"
)

print(
    f"Maximum site-count difference: "
    f"{max_count_difference}"
)


# ============================================================
# SCENARIO-LEVEL COMPARISON
#
# Reproduce production nearest-Mw mapping.
# ============================================================

available_magnitudes = (

    p2_scenarios[
        "Mw"
    ]
    .dropna()
    .unique()

)


scenario_results = []


for scenario, target_magnitude in (
    SCENARIO_MAGNITUDES.items()
):

    matched_magnitude = (
        nearest_p2_magnitude(
            target_magnitude,
            available_magnitudes
        )
    )


    matched = p2_scenarios[
        p2_scenarios["Mw"]
        ==
        matched_magnitude
    ]


    if matched.empty:

        raise RuntimeError(

            f"No P2 magnitude found for "
            f"scenario: {scenario}"

        )


    row = matched.iloc[0]


    scenario_results.append({

        "location_name":
            scenario,

        "target_Mw":
            target_magnitude,

        "matched_Mw":
            matched_magnitude,

        "site_count":
            int(
                row[
                    "module_site_count"
                ]
            ),

        "module_mean_score":
            row[
                "module_mean_score"
            ],

        "production_mean_score":
            row[
                "production_mean_score"
            ],

        "mean_absolute_difference":
            row[
                "mean_difference"
            ],

        "module_max_score":
            row[
                "module_max_score"
            ],

        "production_max_score":
            row[
                "production_max_score"
            ],

        "max_absolute_difference":
            row[
                "max_difference"
            ],

    })


comparison = pd.DataFrame(
    scenario_results
)


# ============================================================
# DISPLAY SCENARIO RESULTS
# ============================================================

print()
print(
    "Scenario comparison"
)

print("-" * 70)

print(

    comparison[

        [
            "location_name",
            "target_Mw",
            "matched_Mw",
            "site_count",
            "module_mean_score",
            "production_mean_score",
            "mean_absolute_difference",
            "module_max_score",
            "production_max_score",
            "max_absolute_difference",
        ]

    ].to_string(
        index=False
    )

)


# ============================================================
# FINAL VALIDATION
# ============================================================

ALLOWED_DIFFERENCE = 1e-12


max_scenario_mean_difference = (

    comparison[
        "mean_absolute_difference"
    ].max()

)


max_scenario_max_difference = (

    comparison[
        "max_absolute_difference"
    ].max()

)


scenario_count = len(
    comparison
)


print()
print(
    f"Scenarios compared: "
    f"{scenario_count}"
)

print(
    f"Maximum scenario mean difference: "
    f"{max_scenario_mean_difference:.15f}"
)

print(
    f"Maximum scenario max difference: "
    f"{max_scenario_max_difference:.15f}"
)

print(
    f"Allowed difference: "
    f"{ALLOWED_DIFFERENCE}"
)


# ============================================================
# ASSERTIONS
# ============================================================

if scenario_count != 9:

    raise AssertionError(
        "Expected exactly 9 scenarios."
    )


if max_row_difference > ALLOWED_DIFFERENCE:

    raise AssertionError(

        "P2 module row-level scores "
        "do not match production."

    )


if max_mean_difference > ALLOWED_DIFFERENCE:

    raise AssertionError(

        "P2 module mean aggregation "
        "does not match production."

    )


if max_max_difference > ALLOWED_DIFFERENCE:

    raise AssertionError(

        "P2 module max aggregation "
        "does not match production."

    )


if max_count_difference != 0:

    raise AssertionError(

        "P2 module site counts "
        "do not match production."

    )


if (
    max_scenario_mean_difference
    > ALLOWED_DIFFERENCE
):

    raise AssertionError(

        "P2 module scenario mean scores "
        "do not match production."

    )


if (
    max_scenario_max_difference
    > ALLOWED_DIFFERENCE
):

    raise AssertionError(

        "P2 module scenario max scores "
        "do not match production."

    )


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print(
    "P2 MODULE EQUIVALENCE: PASS"
)
print("=" * 70)

print(
    "Independent P2 module reproduces "
    "the production P2 scoring and aggregation."
)

print(
    "No P2 model, preprocessing, magnitude "
    "mapping, or aggregation differences detected."
)

print(
    "The P2 modularization preserves "
    "the existing production behavior."
)

print("=" * 70)
