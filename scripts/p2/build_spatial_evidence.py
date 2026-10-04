import pandas as pd
import numpy as np

INPUT = r"outputs\verified_ngl_anchor_evidence.csv"
OUTPUT = r"outputs\p2_spatial_evidence.csv"

df = pd.read_csv(INPUT)


# ---------------------------------------------------------
# 1. Historical outcome signal
# ---------------------------------------------------------
#
# This is an evidence descriptor, NOT a probability.
#
# L_rate:
#   1.0 = all historical observations liquefied
#   0.0 = none liquefied
#
# We shrink extreme values when sample size is very small.
# This prevents one observation from being treated as
# equally strong evidence as a large case-history sample.
# ---------------------------------------------------------

prior_rate = 0.50
prior_strength = 4

df["historical_L_rate_smoothed"] = (
    (
        df["historical_L_rate"] * df["historical_records"]
    )
    + (prior_rate * prior_strength)
) / (
    df["historical_records"] + prior_strength
)


# ---------------------------------------------------------
# 2. Sample-size confidence
# ---------------------------------------------------------

df["sample_size_weight"] = np.sqrt(
    df["historical_records"]
    / (
        df["historical_records"]
        + prior_strength
    )
)


# ---------------------------------------------------------
# 3. Historical evidence component
# ---------------------------------------------------------
#
# Convert the smoothed historical rate from:
#       [0, 1]
#
# into:
#       [-1, +1]
#
# -1 = evidence against liquefaction
#  0 = neutral
# +1 = evidence supporting liquefaction
# ---------------------------------------------------------

historical_signal = (
    2 * df["historical_L_rate_smoothed"] - 1
)

df["historical_evidence_component"] = (
    historical_signal
    * df["sample_size_weight"]
)


# ---------------------------------------------------------
# 4. Spatial lookup quality
# ---------------------------------------------------------

df["spatial_quality_weight"] = np.select(
    [
        df["shakemap_anchor_distance_km"] <= 1.0,
        df["shakemap_anchor_distance_km"] <= 3.0,
    ],
    [
        1.00,
        0.90,
    ],
    default=0.75,
)
# ---------------------------------------------------------
# 4.5 Spatial lookup quality
# ---------------------------------------------------------

df["spatial_lookup_quality"] = np.select(
    [
        df["shakemap_anchor_distance_km"] <= 1.0,
        df["shakemap_anchor_distance_km"] <= 3.0,
    ],
    [
        "HIGH",
        "GOOD",
    ],
    default="CHECK",
)

# ---------------------------------------------------------
# 5. ShakeMap PGA context
# ---------------------------------------------------------
#
# IMPORTANT:
# PGA is NOT converted directly into a probability.
#
# We only retain a normalized logarithmic context value.
# This prevents large PGA values from dominating the
# historical evidence.
# ---------------------------------------------------------

pga_reference = 0.20

df["ShakeMap_PGA_context"] = np.log10(
    df["ShakeMap_PGA_g"] / pga_reference
)

# Limit extreme values.
df["ShakeMap_PGA_context"] = (
    df["ShakeMap_PGA_context"]
    .clip(-1.0, 1.0)
)


# ---------------------------------------------------------
# 6. Combined spatial evidence score
# ---------------------------------------------------------
#
# Historical evidence receives the largest weight.
# PGA is contextual only.
#
# Result approximately ranges from -1 to +1.
#
# Positive  -> evidence supporting liquefaction review
# Negative  -> evidence against liquefaction
# Near zero -> mixed/weak evidence
# ---------------------------------------------------------

df["spatial_evidence_score"] = (
    0.75
    * df["historical_evidence_component"]
    * df["spatial_quality_weight"]
    +
    0.25
    * (
        df["ShakeMap_PGA_context"]
        * 0.5
    )
)


# ---------------------------------------------------------
# 7. Evidence category
# ---------------------------------------------------------

df["spatial_evidence_category"] = np.select(
    [
        df["spatial_evidence_score"] >= 0.35,
        df["spatial_evidence_score"] <= -0.35,
    ],
    [
        "SUPPORTING_LIQUEFACTION_EVIDENCE",
        "NON_LIQUEFACTION_EVIDENCE",
    ],
    default="MIXED_OR_LIMITED_EVIDENCE",
)


# ---------------------------------------------------------
# 8. Human-readable caution
# ---------------------------------------------------------

df["evidence_caution"] = np.where(
    df["historical_records"] < 3,
    "VERY_SMALL_HISTORICAL_SAMPLE",
    np.where(
        df["historical_records"] < 10,
        "LIMITED_HISTORICAL_SAMPLE",
        "LARGER_HISTORICAL_SAMPLE",
    ),
)


# ---------------------------------------------------------
# 9. Keep the important fields
# ---------------------------------------------------------

columns = [
    "scenario",
    "anchor_group",
    "ngl_site",
    "match_level",

    "anchor_latitude",
    "anchor_longitude",

    "anchor_epicenter_distance_km",

    "shakemap_anchor_distance_km",
    "spatial_lookup_quality",

    "historical_records",
    "historical_unique_sites",
    "historical_L_rate",
    "historical_L_rate_smoothed",

    "historical_Mw_min",
    "historical_Mw_max",

    "historical_PGA_mean",
    "historical_PGA_min",
    "historical_PGA_max",

    "ShakeMap_PGA_g",
    "ShakeMap_PGA_context",

    "sample_size_weight",
    "historical_evidence_component",

    "spatial_evidence_score",
    "spatial_evidence_category",

    "evidence_caution",
]


result = df[columns].copy()


# ---------------------------------------------------------
# 10. Print result
# ---------------------------------------------------------

print("\n========================================")
print("P2 SPATIAL EVIDENCE LAYER")
print("========================================")

print(
    result.to_string(index=False)
)


print("\n========================================")
print("CATEGORY COUNTS")
print("========================================")

print(
    result["spatial_evidence_category"]
    .value_counts()
    .to_string()
)


print("\n========================================")
print("SCENARIO SUMMARY")
print("========================================")

summary = (
    result
    .groupby("scenario")
    .agg(
        anchors=("ngl_site", "count"),
        mean_spatial_evidence=(
            "spatial_evidence_score",
            "mean",
        ),
        min_spatial_evidence=(
            "spatial_evidence_score",
            "min",
        ),
        max_spatial_evidence=(
            "spatial_evidence_score",
            "max",
        ),
        mean_ShakeMap_PGA=(
            "ShakeMap_PGA_g",
            "mean",
        ),
        historical_records=(
            "historical_records",
            "sum",
        ),
    )
    .reset_index()
)

print(
    summary.to_string(index=False)
)


# ---------------------------------------------------------
# 11. Save
# ---------------------------------------------------------

result.to_csv(
    OUTPUT,
    index=False,
)

print("\nSaved:", OUTPUT)