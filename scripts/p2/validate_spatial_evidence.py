import pandas as pd
import numpy as np

INPUT = r"outputs\p2_spatial_evidence.csv"

df = pd.read_csv(INPUT)

print("\n========================================")
print("P2 SPATIAL EVIDENCE VALIDATION")
print("========================================")

# ---------------------------------------------------------
# 1. Historical evidence ordering
# ---------------------------------------------------------

print("\n--- HISTORICAL EVIDENCE ORDERING ---")

cols = [
    "scenario",
    "ngl_site",
    "historical_records",
    "historical_L_rate",
    "historical_L_rate_smoothed",
    "historical_evidence_component",
    "ShakeMap_PGA_g",
    "spatial_evidence_score",
]

print(
    df[cols]
    .sort_values(
        "historical_L_rate",
        ascending=False
    )
    .to_string(index=False)
)


# ---------------------------------------------------------
# 2. Compare evidence with and without PGA
# ---------------------------------------------------------

print("\n========================================")
print("PGA CONTRIBUTION DIAGNOSTIC")
print("========================================")

df["score_without_PGA"] = (
    0.75
    * df["historical_evidence_component"]
    * df["spatial_lookup_quality"].map({
        "HIGH": 1.00,
        "GOOD": 0.90,
        "CHECK": 0.75,
    })
)

df["PGA_contribution"] = (
    df["spatial_evidence_score"]
    - df["score_without_PGA"]
)

pga_cols = [
    "scenario",
    "ngl_site",
    "historical_L_rate",
    "historical_records",
    "score_without_PGA",
    "PGA_contribution",
    "spatial_evidence_score",
]

print(
    df[pga_cols]
    .to_string(index=False)
)


# ---------------------------------------------------------
# 3. Identify largest PGA influence
# ---------------------------------------------------------

print("\n========================================")
print("LARGEST PGA CONTRIBUTIONS")
print("========================================")

print(
    df[
        [
            "scenario",
            "ngl_site",
            "ShakeMap_PGA_g",
            "PGA_contribution",
            "spatial_evidence_score",
        ]
    ]
    .sort_values(
        "PGA_contribution",
        key=lambda x: x.abs(),
        ascending=False,
    )
    .head(10)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 4. Sample-size diagnostic
# ---------------------------------------------------------

print("\n========================================")
print("SAMPLE-SIZE DIAGNOSTIC")
print("========================================")

print(
    df[
        [
            "scenario",
            "ngl_site",
            "historical_records",
            "historical_L_rate",
            "historical_L_rate_smoothed",
            "sample_size_weight",
            "historical_evidence_component",
        ]
    ]
    .sort_values("historical_records")
    .to_string(index=False)
)


# ---------------------------------------------------------
# 5. Scenario-level summary
# ---------------------------------------------------------

print("\n========================================")
print("SCENARIO DIAGNOSTIC")
print("========================================")

summary = (
    df.groupby("scenario")
    .agg(
        anchors=("ngl_site", "count"),
        mean_score=(
            "spatial_evidence_score",
            "mean",
        ),
        min_score=(
            "spatial_evidence_score",
            "min",
        ),
        max_score=(
            "spatial_evidence_score",
            "max",
        ),
        mean_historical_rate=(
            "historical_L_rate",
            "mean",
        ),
        mean_records=(
            "historical_records",
            "mean",
        ),
        mean_pga=(
            "ShakeMap_PGA_g",
            "mean",
        ),
    )
    .reset_index()
)

print(
    summary.to_string(index=False)
)


# ---------------------------------------------------------
# 6. Scientific warnings
# ---------------------------------------------------------

print("\n========================================")
print("SCIENTIFIC CHECKS")
print("========================================")

print(
    "\nNOTE:"
    "\n- spatial_evidence_score is a heuristic diagnostic."
    "\n- It is NOT a calibrated probability."
    "\n- Historical L_rate is historical case evidence,"
    "\n  not a future liquefaction probability."
    "\n- ShakeMap PGA is contextual evidence."
    "\n- No fusion with the existing P2 model is performed."
)

print("\nValidation complete.")