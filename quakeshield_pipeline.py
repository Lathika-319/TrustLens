
# ============================================================
# QUAKESHIELD â€” HISTORICAL SECONDARY-HAZARD SCREENING PIPELINE
# ============================================================
#
# CURRENT PROTOTYPE
#
# P1 = Ground-failure model indicator
# P2 = Liquefaction model indicator
# Spatial evidence = historical cases + NGL anchors + ShakeMap PGA
# Infrastructure = mapped infrastructure context
#
# IMPORTANT:
# - No combined risk probability
# - No HIGH/MEDIUM/LOW risk classification
# - No automatic public alerts
# - P1/P2 scores are model indicators, not calibrated probabilities
# - Infrastructure is contextual proximity information
#
# P1 CURRENT MODEL:
# - Slope + PGA
# - slope_degrees
# - PGA_g
# ============================================================

import os
import numpy as np
import pandas as pd

from hazard_modules import (
    ground_failure,
    liquefaction
)

from hazard_registry import (
    get_active_hazard_modules,
    get_context_modules,
    validate_registry
)
# ============================================================
# HAZARD REGISTRY VALIDATION
# ============================================================

registry_errors = validate_registry()

if registry_errors:

    print("ERROR: Hazard registry validation failed.")

    for error in registry_errors:
        print(f"  - {error}")

    raise RuntimeError(
        "QuakeShield hazard registry is invalid."
    )

active_hazard_modules = get_active_hazard_modules()
context_modules = get_context_modules()

print(
    "Hazard registry loaded:",
    ", ".join(
        module["id"]
        for module in active_hazard_modules
    )
)

print(
    "Context modules loaded:",
    ", ".join(
        module["id"]
        for module in context_modules
    )
)
# ============================================================
# 1. CONFIGURATION
# ============================================================

P1_MODEL_FILE = r"models\p1_ground_failure_model_slope_pga.joblib"
P2_MODEL_FILE = r"models\p2_liquefaction_model.joblib"

P1_FILE = r"data\QuakeShield_Final_Dataset_Slope_PGA.csv"
P2_FILE = r"data\raw\Database 7.xlsx"

INFRASTRUCTURE_FILE = r"outputs\infrastructure_risk.csv"
SPATIAL_CONTEXT_FILE = r"outputs\p2_review_context.csv"

FINAL_OUTPUT_FILE = r"outputs\quakeshield_final_output.csv"
MAP_OUTPUT_FILE = r"outputs\quakeshield_map_data.csv"
EXPLANATION_OUTPUT_FILE = r"outputs\quakeshield_explanations.csv"


# ============================================================
# 2. OUTPUT DIRECTORY
# ============================================================

os.makedirs("outputs", exist_ok=True)


# ============================================================
# 3. HELPERS
# ============================================================

def safe_read_csv(path):

    if not os.path.exists(path):
        print(f"WARNING: File not found: {path}")
        return pd.DataFrame()

    try:
        return pd.read_csv(path)

    except Exception as exc:
        print(f"WARNING: Could not read {path}")
        print(exc)
        return pd.DataFrame()


def clean_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def format_distance(value):

    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):.2f} km"

    except Exception:
        return str(value)


def model_score_description(value):

    if pd.isna(value):
        return "not available"

    return f"{float(value):.3f}"


# ============================================================
# 4. HEADER
# ============================================================

print()
print("============================================================")
print("QUAKESHIELD PIPELINE")
print("============================================================")


# ============================================================
# 5. LOAD P1 MODEL
# ============================================================

print()
print("Loading P1 ground-failure model...")

if not os.path.exists(P1_MODEL_FILE):

    raise FileNotFoundError(
        f"P1 model not found: {P1_MODEL_FILE}"
    )

p1_model = ground_failure.load_model(
    P1_MODEL_FILE
)

print(
    f"P1 model loaded: {P1_MODEL_FILE}"
)

print(
    "P1 features: slope_degrees + PGA_g"
)


# ============================================================
# 6. LOAD P1 DATASET
# ============================================================

print()
print("Loading P1 dataset...")

if not os.path.exists(P1_FILE):

    raise FileNotFoundError(
        f"P1 dataset not found: {P1_FILE}"
    )

p1_data = pd.read_csv(
    P1_FILE
)

print(
    f"P1 rows: {len(p1_data):,}"
)


# ============================================================
# 7. VERIFY ACTUAL P1 COLUMNS
# ============================================================

required_p1_columns = [

    "grid_x",
    "grid_y",

    "longitude",
    "latitude",

    "label",
    "label_name",

    "earthquake_id",
    "earthquake_name",
    "earthquake_date",

    "earthquake_magnitude",
    "earthquake_latitude",
    "earthquake_longitude",
    "earthquake_depth_km",

    "mapping_confidence",

    "distance_to_epicenter_km",

    "elevation_m",

    "slope_degrees",

    "PGA_g"
]


missing_p1_columns = [

    column
    for column in required_p1_columns
    if column not in p1_data.columns

]


if missing_p1_columns:

    raise ValueError(
        "Missing P1 columns: "
        + ", ".join(missing_p1_columns)
    )


# ============================================================
# 8. P1 NUMERIC CLEANING
# ============================================================

numeric_p1_columns = [

    "longitude",
    "latitude",

    "earthquake_magnitude",

    "earthquake_latitude",
    "earthquake_longitude",

    "earthquake_depth_km",

    "distance_to_epicenter_km",

    "elevation_m",

    "slope_degrees",

    "PGA_g"

]


for column in numeric_p1_columns:

    p1_data[column] = clean_numeric(
        p1_data[column]
    )


# ============================================================
# 9. P1 MODEL PREDICTION
# ============================================================

print()
print("Running P1 ground-failure model...")
print("Features: slope_degrees + PGA_g")

p1_features = p1_data[
    [
        "slope_degrees",
        "PGA_g"
    ]
].copy()


p1_scores = ground_failure.predict_scores(
    p1_features,
    model=p1_model
)


p1_data[
    "P1_model_score"
] = p1_scores


# ============================================================
# 10. AGGREGATE P1 BY EARTHQUAKE
# ============================================================

p1_group_columns = [

    "earthquake_id",

    "earthquake_name",

    "earthquake_date",

    "earthquake_magnitude",

    "earthquake_latitude",

    "earthquake_longitude",

    "earthquake_depth_km"

]


p1_scenarios = (

    p1_data

    .groupby(
        p1_group_columns,
        dropna=False
    )

    .agg(

        P1_ground_failure_score=(
            "P1_model_score",
            "mean"
        ),

        P1_sample_count=(
            "P1_model_score",
            "count"
        )

    )

    .reset_index()

)


# ============================================================
# 11. RENAME SCENARIO FIELDS
# ============================================================

p1_scenarios = (

    p1_scenarios

    .rename(
        columns={

            "earthquake_name":
                "location_name",

            "earthquake_magnitude":
                "magnitude",

            "earthquake_latitude":
                "latitude",

            "earthquake_longitude":
                "longitude"

        }
    )

)


print(
    f"P1 earthquake scenarios: "
    f"{len(p1_scenarios)}"
)


# ============================================================
# 12. LOAD P2 MODEL
# ============================================================

print()
print("Loading P2 liquefaction model...")

if not os.path.exists(P2_MODEL_FILE):

    raise FileNotFoundError(
        f"P2 model not found: {P2_MODEL_FILE}"
    )


p2_model = liquefaction.load_model(
    P2_MODEL_FILE
)


print(
    f"P2 model loaded: {P2_MODEL_FILE}"
)


# ============================================================
# 13. LOAD P2 DATASET
# ============================================================

print()
print("Loading P2 liquefaction dataset...")

if not os.path.exists(P2_FILE):

    raise FileNotFoundError(
        f"P2 dataset not found: {P2_FILE}"
    )


p2_data = pd.read_excel(
    P2_FILE,
    sheet_name="Liq database"
)


print(
    f"P2 rows: {len(p2_data):,}"
)


# ============================================================
# 14. P2 FEATURES
# ============================================================

p2_base_features = [

    "Ïƒv/Ïƒv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)"

]


p2_missing_source_features = [

    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"

]


# ============================================================
# 15. VERIFY P2 COLUMNS
# ============================================================

missing_p2_columns = [

    column

    for column
    in p2_base_features

    if column
    not in p2_data.columns

]


if missing_p2_columns:

    raise ValueError(
        "Missing P2 columns: "
        + ", ".join(missing_p2_columns)
    )


# ============================================================
# 16. CREATE P2 MISSINGNESS FEATURES
# ============================================================

for column in p2_missing_source_features:

    missing_column = (
        f"{column}_missing"
    )

    p2_data[
        missing_column
    ] = (

        p2_data[column]

        .isna()

        .astype(int)

    )


# ============================================================
# 17. CLEAN P2 NUMERIC FEATURES
# ============================================================

for column in p2_base_features:

    p2_data[column] = clean_numeric(
        p2_data[column]
    )


# ============================================================
# 18. P2 FEATURE LIST
# ============================================================

p2_feature_columns = (

    p2_base_features

    +

    [
        f"{column}_missing"
        for column
        in p2_missing_source_features
    ]

)


# ============================================================
# 19. RUN P2 MODEL
# ============================================================

print()
print("Running P2 liquefaction model...")


p2_scores = liquefaction.predict_scores(
    p2_data[
        p2_feature_columns
    ],
    model=p2_model
)


p2_data[
    "P2_model_score"
] = p2_scores


# ============================================================
# 20. AGGREGATE P2 BY MAGNITUDE
# ============================================================

p2_scenarios = (

    p2_data

    .groupby(
        "Mw",
        dropna=False
    )

    .agg(

        mean_P2_liquefaction_model_score=(

            "P2_model_score",
            "mean"

        ),

        max_P2_liquefaction_model_score=(

            "P2_model_score",
            "max"

        ),

        p2_site_count=(

            "P2_model_score",
            "count"

        )

    )

    .reset_index()

)


print(
    f"P2 magnitude scenarios: "
    f"{len(p2_scenarios)}"
)


# ============================================================
# 21. FIND NEAREST P2 MAGNITUDE
# ============================================================

def nearest_p2_magnitude(magnitude):

    if pd.isna(magnitude):

        return np.nan


    valid_magnitudes = (

        p2_scenarios[
            "Mw"
        ]

        .dropna()

        .unique()

    )


    if len(valid_magnitudes) == 0:

        return np.nan


    return min(

        valid_magnitudes,

        key=lambda value:
            abs(
                float(value)
                -
                float(magnitude)
            )

    )


p1_scenarios[
    "matched_P2_Mw"
] = (

    p1_scenarios[
        "magnitude"
    ]

    .apply(
        nearest_p2_magnitude
    )

)


# ============================================================
# 22. COMBINE P1 + P2
# ============================================================

fusion = p1_scenarios.merge(

    p2_scenarios,

    left_on="matched_P2_Mw",

    right_on="Mw",

    how="left"

)


if "Mw" in fusion.columns:

    fusion.drop(
        columns=["Mw"],
        inplace=True
    )


# ============================================================
# 23. LOAD SPATIAL REVIEW CONTEXT
# ============================================================

print()
print("Loading spatial review context...")


spatial_context = safe_read_csv(
    SPATIAL_CONTEXT_FILE
)


print(
    f"Spatial context rows: "
    f"{len(spatial_context)}"
)


# ============================================================
# 24. MATCH SPATIAL CONTEXT
# ============================================================

scenario_map = {

    "Tohoku-Oki, Japan":
        "Tohoku-Oki",

    "Kobe, Japan":
        "Kobe",

    "Niigata-Chuetsu, Japan":
        "Niigata-Chuetsu"

}


fusion[
    "spatial_evidence_scenario"
] = (

    fusion[
        "location_name"
    ]

    .map(
        scenario_map
    )

)


fusion[
    "spatial_anchor_count"
] = np.nan


fusion[
    "spatial_historical_records"
] = np.nan


fusion[
    "spatial_mean_ShakeMap_PGA"
] = np.nan


fusion[
    "spatial_mean_historical_L_rate"
] = np.nan


fusion[
    "spatial_evidence_available"
] = False


if not spatial_context.empty:

    spatial_context_columns = [

        "spatial_evidence_scenario",

        "spatial_anchor_count",

        "spatial_historical_records",

        "spatial_mean_ShakeMap_PGA",

        "spatial_mean_historical_L_rate",

        "spatial_evidence_available"

    ]


    available_spatial_columns = [

        column

        for column
        in spatial_context_columns

        if column
        in spatial_context.columns

    ]


    if (
        "spatial_evidence_scenario"
        in available_spatial_columns
    ):

        spatial_lookup = (

            spatial_context[
                available_spatial_columns
            ]

            .drop_duplicates(

                subset=[
                    "spatial_evidence_scenario"
                ]

            )

            .set_index(
                "spatial_evidence_scenario"
            )

        )


        for column in [

            "spatial_anchor_count",

            "spatial_historical_records",

            "spatial_mean_ShakeMap_PGA",

            "spatial_mean_historical_L_rate"

        ]:

            if (
                column
                in spatial_lookup.columns
            ):

                fusion[column] = (

                    fusion[
                        "spatial_evidence_scenario"
                    ]

                    .map(
                        spatial_lookup[column]
                    )

                )


        if (
            "spatial_evidence_available"
            in spatial_lookup.columns
        ):

            fusion[
                "spatial_evidence_available"
            ] = (

                fusion[
                    "spatial_evidence_scenario"
                ]

                .map(

                    spatial_lookup[
                        "spatial_evidence_available"
                    ]

                )

                .fillna(False)

                .astype(bool)

            )


# ============================================================
# 25. KEEP P1 AND P2 SEPARATE
# ============================================================

fusion[
    "p1_indicator"
] = (

    fusion[
        "P1_ground_failure_score"
    ]

)


fusion[
    "p2_indicator"
] = (

    fusion[
        "mean_P2_liquefaction_model_score"
    ]

)


fusion[
    "review_status"
] = (

    "REVIEW USING SEPARATE HAZARD INDICATORS"

)


# ============================================================
# 26. LOAD INFRASTRUCTURE CONTEXT
# ============================================================

print()
print("Loading infrastructure context...")


infrastructure = safe_read_csv(
    INFRASTRUCTURE_FILE
)


print(
    f"Infrastructure rows: "
    f"{len(infrastructure)}"
)


# ============================================================
# 27. MERGE INFRASTRUCTURE
# ============================================================

infrastructure_columns = [

    "earthquake_id",

    "location_name",

    "infrastructure_count",

    "nearest_infrastructure_distance_km",

    "hospital_count",

    "school_count",

    "bridge_count",

    "road_count"

]


if not infrastructure.empty:

    available_infrastructure_columns = [

        column

        for column
        in infrastructure_columns

        if column
        in infrastructure.columns

    ]


    infrastructure_lookup = (

        infrastructure[
            available_infrastructure_columns
        ]

        .drop_duplicates()

    )


    merge_keys = [

        column

        for column in [

            "earthquake_id",

            "location_name"

        ]

        if (

            column in fusion.columns

            and

            column in infrastructure_lookup.columns

        )

    ]


    if merge_keys:

        fusion = fusion.merge(

            infrastructure_lookup,

            on=merge_keys,

            how="left",

            suffixes=(
                "",
                "_infra"
            )

        )


# ============================================================
# 28. ENSURE INFRASTRUCTURE COLUMNS EXIST
# ============================================================

infrastructure_numeric_columns = [

    "infrastructure_count",

    "nearest_infrastructure_distance_km",

    "hospital_count",

    "school_count",

    "bridge_count",

    "road_count"

]


for column in infrastructure_numeric_columns:

    if column not in fusion.columns:

        fusion[column] = np.nan


# ============================================================
# 29. REVIEW CONTEXT
# ============================================================

fusion[
    "review_context"
] = np.where(

    fusion[
        "spatial_evidence_available"
    ],

    "SPATIAL EVIDENCE AVAILABLE FOR REVIEW",

    "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE"

)


# Compatibility field only.
# NOT a risk level.

fusion[
    "priority_level"
] = fusion[
    "review_context"
]


# ============================================================
# 30. GENERATE EXPLANATION
# ============================================================

def generate_explanation(row):

    location = row.get(
        "location_name",
        "Unknown scenario"
    )


    p1_score = row.get(
        "P1_ground_failure_score",
        np.nan
    )


    p2_score = row.get(
        "mean_P2_liquefaction_model_score",
        np.nan
    )


    spatial_available = bool(

        row.get(
            "spatial_evidence_available",
            False
        )

    )


    infrastructure_count = row.get(

        "infrastructure_count",
        np.nan

    )


    nearest_distance = row.get(

        "nearest_infrastructure_distance_km",
        np.nan

    )


    parts = []


    parts.append(

        f"{location}: "

        f"P1 ground-failure model score "

        f"is {model_score_description(p1_score)}."

    )


    parts.append(

        f"P2 liquefaction model score "

        f"is {model_score_description(p2_score)}."

    )


    if spatial_available:

        anchor_count = row.get(

            "spatial_anchor_count",
            np.nan

        )


        historical_records = row.get(

            "spatial_historical_records",
            np.nan

        )


        mean_pga = row.get(

            "spatial_mean_ShakeMap_PGA",
            np.nan

        )


        historical_l_rate = row.get(

            "spatial_mean_historical_L_rate",
            np.nan

        )


        parts.append(

            "Verified spatial evidence is available "
            "for review."

        )


        if not pd.isna(anchor_count):

            parts.append(

                f"{int(anchor_count)} mapped anchors "
                f"and "
                f"{int(historical_records) if not pd.isna(historical_records) else 0} "
                f"historical records are represented."

            )


        if not pd.isna(mean_pga):

            parts.append(

                f"Mean current ShakeMap PGA across "
                f"the anchors is {mean_pga:.3f} g."

            )


        if not pd.isna(historical_l_rate):

            parts.append(

                f"Historical liquefaction outcome rate "
                f"across the matched evidence is "
                f"{historical_l_rate:.3f}."

            )


    else:

        parts.append(

            "No verified spatial evidence is "
            "available for this scenario in the "
            "current prototype."

        )


    if not pd.isna(infrastructure_count):

        parts.append(

            f"Mapped infrastructure query returned "
            f"{int(infrastructure_count)} features."

        )


    if not pd.isna(nearest_distance):

        parts.append(

            "Nearest mapped infrastructure feature "
            f"is approximately "
            f"{format_distance(nearest_distance)}."

        )


    parts.append(

        "These outputs are screening indicators "
        "and review context, not calibrated "
        "probabilities, damage estimates, or "
        "automatic alerts."

    )


    return " ".join(parts)


fusion[
    "explanation"
] = fusion.apply(
    generate_explanation,
    axis=1
)


# ============================================================
# 31. FINAL OUTPUT COLUMNS
# ============================================================

final_columns = [

    "earthquake_id",

    "location_name",

    "earthquake_date",

    "latitude",

    "longitude",

    "magnitude",

    "earthquake_depth_km",

    "P1_ground_failure_score",

    "matched_P2_Mw",

    "mean_P2_liquefaction_model_score",

    "max_P2_liquefaction_model_score",

    "p2_site_count",

    "spatial_evidence_scenario",

    "spatial_anchor_count",

    "spatial_historical_records",

    "spatial_mean_ShakeMap_PGA",

    "spatial_mean_historical_L_rate",

    "spatial_evidence_available",

    "infrastructure_count",

    "nearest_infrastructure_distance_km",

    "hospital_count",

    "school_count",

    "bridge_count",

    "road_count",

    "review_context",

    "priority_level",

    "explanation"

]


final_columns = [

    column

    for column
    in final_columns

    if column
    in fusion.columns

]


final = fusion[
    final_columns
].copy()


# ============================================================
# 32. SAVE FINAL OUTPUT
# ============================================================

final.to_csv(

    FINAL_OUTPUT_FILE,

    index=False

)


print()
print(
    f"Final output saved: "
    f"{FINAL_OUTPUT_FILE}"
)


# ============================================================
# 33. MAP OUTPUT
# ============================================================

map_columns = [

    "earthquake_id",

    "location_name",

    "latitude",

    "longitude",

    "magnitude",

    "P1_ground_failure_score",

    "mean_P2_liquefaction_model_score",

    "max_P2_liquefaction_model_score",

    "spatial_evidence_available",

    "spatial_anchor_count",

    "spatial_historical_records",

    "spatial_mean_ShakeMap_PGA",

    "spatial_mean_historical_L_rate",

    "infrastructure_count",

    "nearest_infrastructure_distance_km",

    "review_context",

    "explanation"

]


map_columns = [

    column

    for column
    in map_columns

    if column
    in final.columns

]


map_data = final[
    map_columns
].copy()


map_data.to_csv(

    MAP_OUTPUT_FILE,

    index=False

)


print(

    f"Map output saved: "
    f"{MAP_OUTPUT_FILE}"

)


# ============================================================
# 34. EXPLANATION OUTPUT
# ============================================================

explanation_columns = [

    "earthquake_id",

    "location_name",

    "review_context",

    "explanation"

]


explanation_columns = [

    column

    for column
    in explanation_columns

    if column
    in final.columns

]


explanations = final[
    explanation_columns
].copy()


explanations.to_csv(

    EXPLANATION_OUTPUT_FILE,

    index=False

)


print(

    f"Explanation output saved: "
    f"{EXPLANATION_OUTPUT_FILE}"

)


# ============================================================
# 35. SCENARIO SIDE-BY-SIDE DISPLAY
# ============================================================

print()
print("============================================================")
print("SCENARIO INDICATORS")
print("============================================================")


display_columns = [

    "location_name",

    "P1_ground_failure_score",

    "mean_P2_liquefaction_model_score",

    "spatial_evidence_available",

    "spatial_anchor_count",

    "spatial_historical_records",

    "spatial_mean_ShakeMap_PGA",

    "spatial_mean_historical_L_rate",

    "infrastructure_count",

    "review_context"

]


display_columns = [

    column

    for column
    in display_columns

    if column
    in final.columns

]


print(

    final[
        display_columns
    ]

    .to_string(
        index=False
    )

)


# ============================================================
# 36. FINAL VALIDATION
# ============================================================

print()
print("============================================================")
print("FINAL VALIDATION")
print("============================================================")


print(
    f"Earthquake scenarios: {len(final)}"
)


if len(final) != 9:

    print(
        "WARNING: Expected 9 scenarios."
    )

else:

    print(
        "Scenario count check: PASS"
    )


if "risk_level" in final.columns:

    print(
        "WARNING: risk_level still exists!"
    )

else:

    print(
        "risk_level removal check: PASS"
    )


if "final_risk_score" in final.columns:

    print(
        "WARNING: final_risk_score still exists!"
    )

else:

    print(
        "final_risk_score removal check: PASS"
    )


print()
print(
    "Spatial evidence scenarios:"
)


spatial_scenarios = (

    final.loc[

        final[
            "spatial_evidence_available"
        ],

        "location_name"

    ]

    .tolist()

)


if spatial_scenarios:

    for scenario in spatial_scenarios:

        print(
            f"  - {scenario}"
        )

else:

    print(
        "  None"
    )


# ============================================================
# 37. PIPELINE SUMMARY
# ============================================================

print()
print("============================================================")
print("QUAKESHIELD PIPELINE COMPLETED")
print("============================================================")


print(
    "P1: Ground-failure model indicator "
    "(Slope + PGA)"
)


print(
    "P2: Liquefaction model indicator"
)


print(
    "Spatial evidence: Historical cases + "
    "verified NGL anchors + USGS ShakeMap PGA"
)


print(
    "Infrastructure: Mapped proximity context"
)


print(
    "Combined risk score: NOT USED"
)


print(
    "Risk levels: NOT USED"
)


print(
    "Automatic alerts: NOT USED"
)


print(
    "Interpretation: Human review required"
)


print("============================================================")
