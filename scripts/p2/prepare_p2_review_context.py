import pandas as pd

P2_INPUT = r"outputs\risk_fusion_inputs.csv"
SPATIAL_INPUT = r"outputs\p2_spatial_evidence_final.csv"
OUTPUT = r"outputs\p2_review_context.csv"

p2 = pd.read_csv(P2_INPUT)
spatial = pd.read_csv(SPATIAL_INPUT)

print("\n========================================")
print("P2 REVIEW CONTEXT")
print("========================================")

# ---------------------------------------------------------
# Explicit, verified mapping.
#
# Only scenarios for which we have verified spatial
# evidence are mapped.
# ---------------------------------------------------------

scenario_map = {
    "Tohoku-Oki, Japan": "Tohoku-Oki",
    "Kobe, Japan": "Kobe",
    "Niigata-Chuetsu, Japan": "Niigata-Chuetsu",
}

p2["spatial_evidence_scenario"] = (
    p2["location_name"]
    .map(scenario_map)
)


# ---------------------------------------------------------
# Scenario-level spatial context.
#
# IMPORTANT:
# These are descriptive context fields only.
# They are NOT converted into a new hazard score.
# ---------------------------------------------------------

spatial_summary = (
    spatial
    .groupby("scenario")
    .agg(
        spatial_anchor_count=("ngl_site", "count"),
        spatial_historical_records=(
            "historical_records",
            "sum",
        ),
        spatial_mean_ShakeMap_PGA=(
            "ShakeMap_PGA_g",
            "mean",
        ),
        spatial_mean_historical_L_rate=(
            "historical_L_rate",
            "mean",
        ),
    )
    .reset_index()
)


# ---------------------------------------------------------
# Join spatial context only where an explicit verified
# mapping exists.
# ---------------------------------------------------------

result = p2.merge(
    spatial_summary,
    left_on="spatial_evidence_scenario",
    right_on="scenario",
    how="left",
)

# Remove duplicate scenario column created by merge.
result = result.drop(columns=["scenario"])


# ---------------------------------------------------------
# Evidence availability
# ---------------------------------------------------------

result["spatial_evidence_available"] = (
    result["spatial_anchor_count"]
    .fillna(0)
    .gt(0)
)


print("\n========================================")
print("MAPPING")
print("========================================")

print(
    result[
        [
            "location_name",
            "spatial_evidence_scenario",
            "spatial_evidence_available",
        ]
    ].to_string(index=False)
)


print("\n========================================")
print("P2 REVIEW CONTEXT")
print("========================================")

print(result.to_string(index=False))


result.to_csv(
    OUTPUT,
    index=False,
)

print("\nSaved:", OUTPUT)

print("\nIMPORTANT:")
print("- Existing P2 model scores were not changed.")
print("- Spatial evidence was not converted into a probability.")
print("- No multiplication or averaging of hazard scores was performed.")
print("- Scenarios without verified spatial evidence remain unavailable.")