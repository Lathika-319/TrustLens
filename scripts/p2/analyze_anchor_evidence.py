import pandas as pd
import numpy as np

INPUT = r"outputs\verified_ngl_anchor_evidence.csv"
OUT = r"outputs\p2_anchor_evidence_summary.csv"

df = pd.read_csv(INPUT)

# Historical outcome consistency
df["historical_outcome_strength"] = np.where(
    df["historical_L_rate"] >= 0.75,
    "STRONG_LIQUEFACTION_EVIDENCE",
    np.where(
        df["historical_L_rate"] <= 0.25,
        "STRONG_NON_LIQUEFACTION_EVIDENCE",
        "MIXED_EVIDENCE",
    ),
)

# Evidence sample-size strength
df["sample_size_class"] = np.where(
    df["historical_records"] >= 10,
    "LARGE",
    np.where(
        df["historical_records"] >= 3,
        "SMALL",
        "VERY_SMALL",
    ),
)

# Difference between current-event shaking and historical case-history PGA
df["ShakeMap_vs_historical_PGA_ratio"] = (
    df["ShakeMap_PGA_g"]
    / df["historical_PGA_mean"]
)

# Absolute difference in PGA
df["ShakeMap_minus_historical_PGA_g"] = (
    df["ShakeMap_PGA_g"]
    - df["historical_PGA_mean"]
)

# Spatial confidence based only on how close the
# actual ShakeMap grid point is to the verified anchor.
df["spatial_lookup_quality"] = np.where(
    df["shakemap_anchor_distance_km"] <= 1,
    "HIGH",
    np.where(
        df["shakemap_anchor_distance_km"] <= 3,
        "GOOD",
        "CHECK",
    ),
)

# IMPORTANT:
# This is NOT a hazard probability.
# It is only a transparent evidence descriptor.
df["evidence_summary"] = (
    df["historical_outcome_strength"]
    + " | "
    + df["sample_size_class"]
    + " | "
    + df["spatial_lookup_quality"]
)

columns = [
    "scenario",
    "anchor_group",
    "ngl_site",
    "match_level",
    "anchor_epicenter_distance_km",
    "shakemap_anchor_distance_km",
    "ShakeMap_PGA_g",
    "historical_records",
    "historical_unique_sites",
    "historical_L_rate",
    "historical_PGA_mean",
    "historical_PGA_min",
    "historical_PGA_max",
    "historical_Mw_min",
    "historical_Mw_max",
    "ShakeMap_vs_historical_PGA_ratio",
    "ShakeMap_minus_historical_PGA_g",
    "spatial_lookup_quality",
    "historical_outcome_strength",
    "sample_size_class",
    "evidence_summary",
]

result = df[columns].copy()

print("\n========================================")
print("P2 SPATIAL EVIDENCE ANALYSIS")
print("========================================")

print(result.to_string(index=False))

print("\n========================================")
print("SUMMARY BY SCENARIO")
print("========================================")

scenario_summary = (
    result
    .groupby("scenario")
    .agg(
        anchors=("ngl_site", "count"),
        historical_records=("historical_records", "sum"),
        mean_historical_L_rate=("historical_L_rate", "mean"),
        mean_historical_PGA=("historical_PGA_mean", "mean"),
        mean_ShakeMap_PGA=("ShakeMap_PGA_g", "mean"),
        mean_anchor_distance_km=(
            "anchor_epicenter_distance_km",
            "mean",
        ),
        mean_shakemap_lookup_distance_km=(
            "shakemap_anchor_distance_km",
            "mean",
        ),
    )
    .reset_index()
)

print(
    scenario_summary.to_string(index=False)
)

print("\n========================================")
print("EVIDENCE COUNTS")
print("========================================")

print(
    result["evidence_summary"]
    .value_counts()
    .to_string()
)

result.to_csv(
    OUT,
    index=False,
)

print("\nSaved:", OUT)