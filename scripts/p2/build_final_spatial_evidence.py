import pandas as pd
import numpy as np

INPUT = r"outputs\verified_ngl_anchor_evidence.csv"
OUTPUT = r"outputs\p2_spatial_evidence_final.csv"

df = pd.read_csv(INPUT)


# =========================================================
# 1. Historical evidence strength
# =========================================================
#
# This describes the amount of historical case evidence.
# It is NOT a probability.
# =========================================================

df["historical_evidence_strength"] = np.select(
    [
        df["historical_records"] >= 10,
        df["historical_records"] >= 3,
    ],
    [
        "LARGE",
        "LIMITED",
    ],
    default="VERY_SMALL",
)


# =========================================================
# 2. Historical outcome description
# =========================================================
#
# Describe what the historical observations show.
# Avoid calling this a predicted probability.
# =========================================================

df["historical_outcome"] = np.select(
    [
        df["historical_L_rate"] >= 0.75,
        df["historical_L_rate"] <= 0.25,
    ],
    [
        "MOST_HISTORICAL_CASES_LIQUEFIED",
        "MOST_HISTORICAL_CASES_DID_NOT_LIQUEFY",
    ],
    default="MIXED_HISTORICAL_OUTCOMES",
)


# =========================================================
# 3. ShakeMap lookup quality
# =========================================================
#
# Based only on distance from the verified NGL anchor
# to the nearest ShakeMap grid location.
# =========================================================

df["ShakeMap_lookup_quality"] = np.select(
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


# =========================================================
# 4. Historical PGA vs current ShakeMap PGA
# =========================================================
#
# Keep these as separate observations.
#
# IMPORTANT:
# We do NOT interpret their ratio as probability,
# model accuracy, or hazard severity.
# =========================================================

df["PGA_comparison"] = np.select(
    [
        df["ShakeMap_PGA_g"]
        > df["historical_PGA_max"],

        df["ShakeMap_PGA_g"]
        < df["historical_PGA_min"],
    ],
    [
        "CURRENT_PGA_ABOVE_HISTORICAL_RANGE",
        "CURRENT_PGA_BELOW_HISTORICAL_RANGE",
    ],
    default="CURRENT_PGA_WITHIN_HISTORICAL_RANGE",
)


# =========================================================
# 5. Historical magnitude comparison
# =========================================================
#
# The current scenario magnitude is not available in this
# evidence table, so we retain the historical magnitude
# range only.
# =========================================================

df["historical_magnitude_context"] = (
    df["historical_Mw_min"].round(1).astype(str)
    + "–"
    + df["historical_Mw_max"].round(1).astype(str)
)


# =========================================================
# 6. Overall evidence review label
# =========================================================
#
# This is a REVIEW DESCRIPTION, not a hazard score.
# =========================================================

df["review_evidence_level"] = np.select(
    [
        (
            (df["historical_records"] >= 10)
            & (df["historical_L_rate"] >= 0.75)
        ),

        (
            (df["historical_records"] >= 10)
            & (df["historical_L_rate"] <= 0.25)
        ),

        (
            (df["historical_records"] >= 10)
            & (df["historical_L_rate"] > 0.25)
            & (df["historical_L_rate"] < 0.75)
        ),
    ],
    [
        "STRONG_HISTORICAL_SUPPORT",
        "STRONG_HISTORICAL_NON_SUPPORT",
        "MIXED_HISTORICAL_EVIDENCE",
    ],
    default="LIMITED_HISTORICAL_EVIDENCE",
)


# =========================================================
# 7. Human-review note
# =========================================================

df["review_note"] = np.select(
    [
        df["historical_records"] < 3,

        (
            (df["historical_records"] >= 3)
            & (df["historical_L_rate"] >= 0.75)
        ),

        (
            (df["historical_records"] >= 3)
            & (df["historical_L_rate"] <= 0.25)
        ),
    ],
    [
        "Historical sample is very small; treat as contextual evidence only.",

        "Historical case records provide supporting context for further review.",

        "Historical case records provide non-liquefaction context; do not treat as a safety clearance.",
    ],
    default="Historical evidence is mixed; review site-specific context.",
)


# =========================================================
# 8. Select final columns
# =========================================================

columns = [
    "scenario",
    "anchor_group",
    "ngl_site",
    "match_level",

    "anchor_latitude",
    "anchor_longitude",

    "anchor_epicenter_distance_km",

    "shakemap_anchor_distance_km",
    "ShakeMap_lookup_quality",

    "ShakeMap_PGA_g",

    "historical_records",
    "historical_unique_sites",
    "historical_L_rate",
    "historical_evidence_strength",
    "historical_outcome",

    "historical_PGA_mean",
    "historical_PGA_min",
    "historical_PGA_max",
    "PGA_comparison",

    "historical_Mw_min",
    "historical_Mw_max",
    "historical_magnitude_context",

    "review_evidence_level",
    "review_note",
]


result = df[columns].copy()


# =========================================================
# 9. Print final evidence layer
# =========================================================

print("\n========================================")
print("FINAL P2 SPATIAL EVIDENCE LAYER")
print("========================================")

print(
    result.to_string(index=False)
)


print("\n========================================")
print("HISTORICAL EVIDENCE LEVELS")
print("========================================")

print(
    result["historical_evidence_strength"]
    .value_counts()
    .to_string()
)


print("\n========================================")
print("HISTORICAL OUTCOMES")
print("========================================")

print(
    result["historical_outcome"]
    .value_counts()
    .to_string()
)


print("\n========================================")
print("PGA COMPARISON")
print("========================================")

print(
    result["PGA_comparison"]
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
        historical_records=("historical_records", "sum"),
        mean_historical_L_rate=(
            "historical_L_rate",
            "mean",
        ),
        mean_historical_PGA=(
            "historical_PGA_mean",
            "mean",
        ),
        mean_current_ShakeMap_PGA=(
            "ShakeMap_PGA_g",
            "mean",
        ),
    )
    .reset_index()
)

print(
    summary.to_string(index=False)
)


# =========================================================
# 10. Save
# =========================================================

result.to_csv(
    OUTPUT,
    index=False,
)

print("\nSaved:", OUTPUT)