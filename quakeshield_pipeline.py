import os
import joblib
import numpy as np
import pandas as pd


# ============================================================
# QUAKESHIELD - END-TO-END PIPELINE
# ============================================================

print("=" * 70)
print("QUAKESHIELD END-TO-END PIPELINE")
print("=" * 70)


# ============================================================
# FILE PATHS
# ============================================================

p1_model_file = r"models\p1_ground_failure_model.joblib"
p2_model_file = r"models\p2_liquefaction_model.joblib"

p1_file = r"data\raw\QuakeShield_Final_Dataset.csv"
p2_file = r"data\raw\Database 7.xlsx"

infrastructure_file = r"outputs\infrastructure_risk.csv"

output_file = r"outputs\quakeshield_final_output.csv"
map_output_file = r"outputs\quakeshield_map_data.csv"
explanation_file = r"outputs\quakeshield_explanations.csv"
risk_input_file = r"outputs\risk_fusion_inputs.csv"


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs("outputs", exist_ok=True)


# ============================================================
# 1. LOAD MODELS
# ============================================================

print("\nLoading trained models...")

p1_model = joblib.load(p1_model_file)
p2_model = joblib.load(p2_model_file)

print("Models loaded successfully.")


# ============================================================
# 2. LOAD P1 DATASET
# ============================================================

print("\nLoading P1 ground-failure dataset...")

p1_df = pd.read_csv(p1_file)

print(f"P1 dataset loaded: {len(p1_df)} rows")


# ============================================================
# 3. P1 FEATURE ENGINEERING
# ============================================================

p1_df["depth_missing"] = (
    p1_df["earthquake_depth_km"]
    .isna()
    .astype(int)
)

p1_df["elevation_missing"] = (
    p1_df["elevation_m"]
    .isna()
    .astype(int)
)

p1_df["magnitude_distance_ratio"] = (
    p1_df["earthquake_magnitude"]
    /
    (p1_df["distance_to_epicenter_km"] + 1)
)

p1_df["magnitude_distance_interaction"] = (
    p1_df["earthquake_magnitude"]
    *
    p1_df["distance_to_epicenter_km"]
)

p1_df["depth_distance_ratio"] = (
    p1_df["earthquake_depth_km"]
    /
    (p1_df["distance_to_epicenter_km"] + 1)
)

p1_df["log_elevation"] = np.log1p(
    np.maximum(
        p1_df["elevation_m"],
        0
    )
)


# ============================================================
# P1 FEATURES
# ============================================================

p1_features = [
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

X_p1 = p1_df[p1_features]


# ============================================================
# 4. P1 PREDICTIONS
# ============================================================

p1_df["P1_ground_failure_probability"] = (
    p1_model.predict_proba(X_p1)[:, 1]
)

print(
    f"P1 predictions completed: "
    f"{len(p1_df)} locations"
)


# ============================================================
# 5. AGGREGATE P1 BY EARTHQUAKE
# ============================================================

p1_scenarios = (
    p1_df
    .groupby(
        [
            "earthquake_id",
            "earthquake_name",
            "earthquake_date"
        ],
        as_index=False
    )
    .agg(
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        P1_ground_failure_probability=(
            "P1_ground_failure_probability",
            "mean"
        )
    )
)

print(
    f"P1 earthquake scenarios: "
    f"{len(p1_scenarios)}"
)


# ============================================================
# 6. LOAD P2 DATASET
# ============================================================

print("\nLoading P2 liquefaction dataset...")

p2_df = pd.read_excel(
    p2_file,
    sheet_name="Liq database"
)

print(
    f"P2 dataset loaded: "
    f"{len(p2_df)} rows"
)


# ============================================================
# 7. CLEAN P2 FC COLUMN
# ============================================================

p2_df["FC (%)"] = pd.to_numeric(
    p2_df["FC (%)"],
    errors="coerce"
)


# ============================================================
# 8. P2 MISSING VALUE FEATURES
# ============================================================

p2_missing_columns = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for column in p2_missing_columns:

    p2_df[column + "_missing"] = (
        p2_df[column]
        .isna()
        .astype(int)
    )


# ============================================================
# 9. P2 FEATURES
# ============================================================

p2_features = [
    "σv/σv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)",
    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"
]

X_p2 = p2_df[p2_features]


# ============================================================
# 10. P2 PREDICTIONS
# ============================================================

p2_df["P2_liquefaction_probability"] = (
    p2_model.predict_proba(X_p2)[:, 1]
)

print(
    f"P2 predictions completed: "
    f"{len(p2_df)} sites"
)


# ============================================================
# 11. AGGREGATE P2 BY MAGNITUDE
# ============================================================

p2_scenarios = (
    p2_df
    .groupby(
        "Mw",
        as_index=False
    )
    .agg(
        mean_P2_liquefaction_probability=(
            "P2_liquefaction_probability",
            "mean"
        ),
        max_P2_liquefaction_probability=(
            "P2_liquefaction_probability",
            "max"
        ),
        p2_site_count=(
            "P2_liquefaction_probability",
            "count"
        )
    )
)

print(
    f"P2 magnitude scenarios: "
    f"{len(p2_scenarios)}"
)


# ============================================================
# 12. MATCH P1 EARTHQUAKE TO NEAREST P2 MAGNITUDE
# ============================================================

def find_nearest_magnitude(magnitude):

    differences = abs(
        p2_scenarios["Mw"]
        - magnitude
    )

    index = differences.idxmin()

    return p2_scenarios.loc[index]


matched_rows = []


for _, row in p1_scenarios.iterrows():

    magnitude = p1_df.loc[
        p1_df["earthquake_id"]
        == row["earthquake_id"],
        "earthquake_magnitude"
    ].iloc[0]

    nearest_p2 = find_nearest_magnitude(
        magnitude
    )

    matched_rows.append(
        {
            "earthquake_id":
                row["earthquake_id"],

            "location_name":
                row["earthquake_name"],

            "earthquake_date":
                row["earthquake_date"],

            "latitude":
                row["latitude"],

            "longitude":
                row["longitude"],

            "magnitude":
                magnitude,

            "P1_ground_failure_probability":
                row[
                    "P1_ground_failure_probability"
                ],

            "matched_P2_Mw":
                nearest_p2["Mw"],

            "mean_P2_liquefaction_probability":
                nearest_p2[
                    "mean_P2_liquefaction_probability"
                ],

            "max_P2_liquefaction_probability":
                nearest_p2[
                    "max_P2_liquefaction_probability"
                ],

            "p2_site_count":
                nearest_p2[
                    "p2_site_count"
                ]
        }
    )


fusion = pd.DataFrame(
    matched_rows
)


# ============================================================
# 13. SAVE RISK FUSION INPUTS
# ============================================================

fusion.to_csv(
    risk_input_file,
    index=False
)


# ============================================================
# 14. RISK FUSION
# ============================================================

fusion["final_risk_score"] = (
    fusion[
        "P1_ground_failure_probability"
    ]
    *
    fusion[
        "mean_P2_liquefaction_probability"
    ]
)


# ============================================================
# 15. RISK LEVEL
# ============================================================

def classify_risk(score):

    if score >= 0.60:
        return "HIGH"

    elif score >= 0.30:
        return "MEDIUM"

    else:
        return "LOW"


fusion["risk_level"] = (
    fusion[
        "final_risk_score"
    ]
    .apply(classify_risk)
)


# ============================================================
# 16. LOAD INFRASTRUCTURE PROXIMITY
# ============================================================

print(
    "\nLoading infrastructure proximity layer..."
)


if os.path.exists(
    infrastructure_file
):

    infrastructure = pd.read_csv(
        infrastructure_file
    )

    print(
        f"Infrastructure records: "
        f"{len(infrastructure)} scenarios"
    )

else:

    print(
        "WARNING: infrastructure_risk.csv "
        "not found."
    )

    infrastructure = pd.DataFrame(
        columns=[
            "earthquake_id",
            "nearby_hospital",
            "nearby_school",
            "nearby_bridge",
            "nearby_road",
            "nearest_hospital_km",
            "nearest_school_km",
            "nearest_bridge_km",
            "nearest_road_km",
            "infrastructure_count"
        ]
    )


# ============================================================
# 17. INFRASTRUCTURE COLUMNS
# ============================================================

infra_columns = [
    "earthquake_id",
    "nearby_hospital",
    "nearby_school",
    "nearby_bridge",
    "nearby_road",
    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km",
    "infrastructure_count"
]


# Keep only columns that actually exist

available_infra_columns = [
    column
    for column in infra_columns
    if column in infrastructure.columns
]


infrastructure = infrastructure[
    available_infra_columns
]


# ============================================================
# 18. MERGE INFRASTRUCTURE
# ============================================================

fusion = fusion.merge(
    infrastructure,
    on="earthquake_id",
    how="left"
)


# ============================================================
# 19. FILL INFRASTRUCTURE FLAGS
# ============================================================

flag_columns = [
    "nearby_hospital",
    "nearby_school",
    "nearby_bridge",
    "nearby_road"
]


for column in flag_columns:

    if column not in fusion.columns:

        fusion[column] = 0

    else:

        fusion[column] = (
            fusion[column]
            .fillna(0)
            .astype(int)
        )


# ============================================================
# 20. FILL INFRASTRUCTURE COUNT
# ============================================================

if "infrastructure_count" not in fusion.columns:

    fusion[
        "infrastructure_count"
    ] = (
        fusion["nearby_hospital"]
        + fusion["nearby_school"]
        + fusion["nearby_bridge"]
        + fusion["nearby_road"]
    )

else:

    fusion[
        "infrastructure_count"
    ] = (
        fusion[
            "infrastructure_count"
        ]
        .fillna(0)
        .astype(int)
    )


# ============================================================
# 21. PRIORITY CLASSIFICATION
# ============================================================

def classify_priority(row):

    risk_level = row[
        "risk_level"
    ]

    infrastructure_count = row[
        "infrastructure_count"
    ]


    if risk_level == "HIGH":

        return "IMMEDIATE ASSESSMENT"


    elif (
        risk_level == "MEDIUM"
        and infrastructure_count > 0
    ):

        return (
            "PRIORITIZE - "
            "INFRASTRUCTURE AT RISK"
        )


    elif risk_level == "MEDIUM":

        return (
            "MONITOR / "
            "FURTHER ASSESSMENT"
        )


    else:

        return "LOWER PRIORITY"


fusion["priority_level"] = (
    fusion
    .apply(
        classify_priority,
        axis=1
    )
)


# ============================================================
# 22. GENERATE EXPLANATIONS
# ============================================================

def format_distance(value):

    if pd.isna(value):

        return "No mapped feature"

    return f"{value:.2f} km"


def generate_explanation(row):

    p1 = row[
        "P1_ground_failure_probability"
    ]

    p2 = row[
        "mean_P2_liquefaction_probability"
    ]

    score = row[
        "final_risk_score"
    ]

    risk = row[
        "risk_level"
    ]

    priority = row[
        "priority_level"
    ]


    hospital_distance = (
        format_distance(
            row.get(
                "nearest_hospital_km",
                np.nan
            )
        )
    )

    school_distance = (
        format_distance(
            row.get(
                "nearest_school_km",
                np.nan
            )
        )
    )

    bridge_distance = (
        format_distance(
            row.get(
                "nearest_bridge_km",
                np.nan
            )
        )
    )

    road_distance = (
        format_distance(
            row.get(
                "nearest_road_km",
                np.nan
            )
        )
    )


    return (
        f"Ground-failure probability is "
        f"{p1:.3f}, while the matched "
        f"liquefaction probability is "
        f"{p2:.3f}. The combined scenario "
        f"risk indicator is {score:.3f}, "
        f"classified as {risk}. "

        f"Nearest mapped hospital: "
        f"{hospital_distance}; "

        f"nearest school: "
        f"{school_distance}; "

        f"nearest bridge: "
        f"{bridge_distance}; "

        f"nearest major road: "
        f"{road_distance}. "

        f"Priority: {priority}."
    )


fusion["explanation"] = (
    fusion
    .apply(
        generate_explanation,
        axis=1
    )
)


# ============================================================
# 23. FINAL OUTPUT
# ============================================================

final_columns = [
    "earthquake_id",
    "location_name",
    "earthquake_date",
    "latitude",
    "longitude",
    "magnitude",

    "P1_ground_failure_probability",

    "matched_P2_Mw",

    "mean_P2_liquefaction_probability",

    "max_P2_liquefaction_probability",

    "p2_site_count",

    "final_risk_score",

    "risk_level",

    "nearby_hospital",
    "nearby_school",
    "nearby_bridge",
    "nearby_road",

    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km",

    "infrastructure_count",

    "priority_level",

    "explanation"
]


# Make sure optional distance columns exist

for column in [
    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km"
]:

    if column not in fusion.columns:

        fusion[column] = np.nan


final = fusion[
    final_columns
].copy()


# ============================================================
# 24. SAVE FINAL OUTPUT
# ============================================================

final.to_csv(
    output_file,
    index=False
)


# ============================================================
# 25. CREATE MAP DATA
# ============================================================

map_columns = [
    "earthquake_id",
    "location_name",
    "earthquake_date",
    "latitude",
    "longitude",
    "magnitude",

    "P1_ground_failure_probability",

    "mean_P2_liquefaction_probability",

    "final_risk_score",

    "risk_level",

    "nearby_hospital",
    "nearby_school",
    "nearby_bridge",
    "nearby_road",

    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km",

    "infrastructure_count",

    "priority_level"
]


map_data = final[
    map_columns
].copy()


map_data.to_csv(
    map_output_file,
    index=False
)


# ============================================================
# 26. SAVE EXPLANATIONS
# ============================================================

explanation_data = final[
    [
        "earthquake_id",
        "location_name",
        "risk_level",
        "priority_level",
        "explanation"
    ]
].copy()


explanation_data.to_csv(
    explanation_file,
    index=False
)


# ============================================================
# 27. DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("QUAKESHIELD PIPELINE COMPLETED")
print("=" * 70)


print(
    f"\nEarthquake scenarios: "
    f"{len(final)}"
)


print("\nRisk distribution:")

print(
    final[
        "risk_level"
    ]
    .value_counts()
    .to_string()
)


print("\nPriority distribution:")

print(
    final[
        "priority_level"
    ]
    .value_counts()
    .to_string()
)


print("\nInfrastructure coverage:")

print(
    f"Hospitals: "
    f"{final['nearby_hospital'].sum()}"
)

print(
    f"Schools: "
    f"{final['nearby_school'].sum()}"
)

print(
    f"Bridges: "
    f"{final['nearby_bridge'].sum()}"
)

print(
    f"Roads: "
    f"{final['nearby_road'].sum()}"
)


# ============================================================
# 28. TOP SCENARIOS
# ============================================================

print("\nTop scenarios:")


display_columns = [
    "location_name",
    "P1_ground_failure_probability",
    "mean_P2_liquefaction_probability",
    "final_risk_score",
    "risk_level",
    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km",
    "priority_level"
]


print(
    final[
        display_columns
    ]
    .sort_values(
        "final_risk_score",
        ascending=False
    )
    .head(5)
    .to_string(index=False)
)


# ============================================================
# 29. OUTPUT FILES
# ============================================================

print("\nSaved:")

print(output_file)
print(map_output_file)
print(explanation_file)
print(risk_input_file)


print("\nPipeline:")

print(
    "Earthquake"
    " → P1 Ground Failure"
    " → P2 Liquefaction"
    " → Risk Fusion"
    " → Risk Level"
    " → Infrastructure Proximity"
    " → Priority"
    " → Explanation"
    " → Map Output"
)


print("\n" + "=" * 70)