import os
import numpy as np
import pandas as pd

BASE = "outputs"

FLDO_FILE = os.path.join(BASE, "ngl_field_observations.csv")
FLDM_FILE = os.path.join(BASE, "ngl_liquefaction_manifestations.csv")
SITES_FILE = os.path.join(BASE, "ngl_sites.csv")
EVENTS_FILE = os.path.join(BASE, "ngl_events.csv")
GMIM_FILE = os.path.join(BASE, "ngl_ground_motion.csv")

OUTPUT_FILE = os.path.join(
    BASE,
    "p4_lateral_spreading_clean_dataset.csv"
)

EVENT_OUTPUT = os.path.join(
    BASE,
    "p4_clean_event_summary.csv"
)


def clean_id(series):
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def numeric(series):
    return pd.to_numeric(series, errors="coerce")


print("=" * 70)
print("QUAKESHIELD — BUILD CLEAN P4 LATERAL SPREADING DATASET")
print("=" * 70)


# ================================================================
# 1. LOAD
# ================================================================

print("\nLoading NGL data...")

fldo = pd.read_csv(FLDO_FILE)
fldm = pd.read_csv(FLDM_FILE)
sites = pd.read_csv(SITES_FILE)
events = pd.read_csv(EVENTS_FILE)
gmim = pd.read_csv(GMIM_FILE)

print(f"Field observations : {len(fldo)}")
print(f"Manifestations     : {len(fldm)}")
print(f"Sites              : {len(sites)}")
print(f"Events             : {len(events)}")
print(f"Ground motion      : {len(gmim)}")


# ================================================================
# 2. NORMALIZE IDS
# ================================================================

fldm["FLDO_ID"] = clean_id(fldm["FLDO_ID"])
fldo["FLDO_ID"] = clean_id(fldo["FLDO_ID"])

fldo["EVNT_ID"] = clean_id(fldo["EVNT_ID"])
fldo["SITE_ID"] = clean_id(fldo["SITE_ID"])

sites["SITE_ID"] = clean_id(sites["SITE_ID"])
events["EVNT_ID"] = clean_id(events["EVNT_ID"])

gmim["FLDO_ID"] = clean_id(gmim["FLDO_ID"])


# ================================================================
# 3. KEEP ONLY USABLE LATERAL-SPREADING LABELS
# ================================================================

print("\n" + "=" * 70)
print("STEP 1 — LABEL FILTER")
print("=" * 70)

manifestations = fldm[
    fldm["FLDM_LTSP"].isin([0, 1])
].copy()

manifestations["ltsp_label"] = (
    manifestations["FLDM_LTSP"]
    .astype(int)
)

print(f"Usable manifestations: {len(manifestations)}")

print(
    manifestations["ltsp_label"]
    .value_counts()
    .sort_index()
)


# ================================================================
# 4. COLLAPSE MANIFESTATIONS TO FIELD OBSERVATION
# ================================================================

print("\n" + "=" * 70)
print("STEP 2 — OBSERVATION-LEVEL LABEL CONSTRUCTION")
print("=" * 70)

observation_labels = (
    manifestations
    .groupby("FLDO_ID")
    .agg(
        positive_count=(
            "ltsp_label",
            lambda x: int((x == 1).sum())
        ),
        negative_count=(
            "ltsp_label",
            lambda x: int((x == 0).sum())
        ),
        manifestation_count=(
            "ltsp_label",
            "count"
        ),
    )
    .reset_index()
)

observation_labels["mixed_label"] = (
    (observation_labels["positive_count"] > 0)
    &
    (observation_labels["negative_count"] > 0)
)

observation_labels["lateral_spreading"] = np.nan

# Positive only
positive_mask = (
    (observation_labels["positive_count"] > 0)
    &
    (observation_labels["negative_count"] == 0)
)

# Negative only
negative_mask = (
    (observation_labels["negative_count"] > 0)
    &
    (observation_labels["positive_count"] == 0)
)

observation_labels.loc[
    positive_mask,
    "lateral_spreading"
] = 1

observation_labels.loc[
    negative_mask,
    "lateral_spreading"
] = 0

print(
    f"Unique usable observations: "
    f"{len(observation_labels)}"
)

print(
    f"Positive-only observations: "
    f"{positive_mask.sum()}"
)

print(
    f"Negative-only observations: "
    f"{negative_mask.sum()}"
)

print(
    f"Mixed-label observations: "
    f"{observation_labels['mixed_label'].sum()}"
)


# ================================================================
# 5. REMOVE AMBIGUOUS MIXED OBSERVATIONS
# ================================================================

clean_labels = observation_labels[
    ~observation_labels["mixed_label"]
].copy()

clean_labels = clean_labels[
    clean_labels["lateral_spreading"].notna()
].copy()

clean_labels["lateral_spreading"] = (
    clean_labels["lateral_spreading"]
    .astype(int)
)

print("\nAfter removing mixed observations:")

print(
    f"Clean observations: "
    f"{len(clean_labels)}"
)

print(
    clean_labels["lateral_spreading"]
    .value_counts()
    .sort_index()
)


# ================================================================
# 6. LINK FIELD OBSERVATION → EVENT / SITE
# ================================================================

print("\n" + "=" * 70)
print("STEP 3 — EVENT / SITE LINKAGE")
print("=" * 70)

obs_columns = [
    "FLDO_ID",
    "EVNT_ID",
    "SITE_ID",
]

clean = clean_labels.merge(
    fldo[obs_columns],
    on="FLDO_ID",
    how="left",
    validate="one_to_one",
)

print(
    "Missing EVNT_ID:",
    clean["EVNT_ID"].isna().sum()
)

print(
    "Missing SITE_ID:",
    clean["SITE_ID"].isna().sum()
)


# ================================================================
# 7. SITE INFORMATION
# ================================================================

site_columns = [
    c
    for c in [
        "SITE_ID",
        "SITE_NAME",
        "SITE_LAT",
        "SITE_LON",
        "SITE_GEOL",
    ]
    if c in sites.columns
]

clean = clean.merge(
    sites[site_columns],
    on="SITE_ID",
    how="left",
    validate="many_to_one",
)


# ================================================================
# 8. EVENT INFORMATION
# ================================================================

event_columns = [
    c
    for c in [
        "EVNT_ID",
        "EVNT_NM",
        "EVNT_YR",
        "EVNT_MAG",
        "HYPO_LAT",
        "HYPO_LON",
    ]
    if c in events.columns
]

clean = clean.merge(
    events[event_columns],
    on="EVNT_ID",
    how="left",
    validate="many_to_one",
)


# ================================================================
# 9. COORDINATES
# ================================================================

clean["latitude"] = numeric(
    clean["SITE_LAT"]
)

clean["longitude"] = numeric(
    clean["SITE_LON"]
)

print("\nCoordinate coverage:")

valid_coords = (
    clean["latitude"].notna()
    &
    clean["longitude"].notna()
)

print(
    f"{valid_coords.sum()}/{len(clean)} "
    f"({100 * valid_coords.mean():.2f}%)"
)


# ================================================================
# 10. NORMALIZE GROUND-MOTION TABLE
# ================================================================

print("\n" + "=" * 70)
print("STEP 4 — GROUND-MOTION NORMALIZATION")
print("=" * 70)

gmim["GMIM_TYPE_CLEAN"] = (
    gmim["GMIM_TYPE"]
    .astype(str)
    .str.strip()
    .str.upper()
)

gmim["GMIM_UNIT_CLEAN"] = (
    gmim["GMIM_UNIT"]
    .astype(str)
    .str.strip()
)

gmim["GMIM_COMP_CLEAN"] = (
    gmim["GMIM_COMP"]
    .astype(str)
    .str.strip()
)

gmim["GMIM_VALUE_NUM"] = numeric(
    gmim["GMIM_VALUE"]
)


# ================================================================
# 11. PGA
# ================================================================

print("\nProcessing PGA...")

pga = gmim[
    gmim["GMIM_TYPE_CLEAN"] == "PGA"
].copy()

# PGA should be in g.
pga = pga[
    pga["GMIM_UNIT_CLEAN"].str.lower() == "g"
].copy()

# Prefer RotD50 / GeoMean / Max / horizontal measurements.
# Do not mix vertical components into the primary PGA feature.
preferred_components = [
    "ROTD50",
    "GEOMEAN",
    "MAX",
    "H1",
    "H2",
]

pga["component_priority"] = (
    pga["GMIM_COMP_CLEAN"]
    .str.upper()
    .map(
        {
            "ROTD50": 1,
            "GEOMEAN": 2,
            "MAX": 3,
            "H1": 4,
            "H2": 5,
        }
    )
    .fillna(99)
)

# For each observation, use the highest-priority component
# when available.
pga = pga.sort_values(
    [
        "FLDO_ID",
        "component_priority",
    ]
)

pga = (
    pga
    .groupby("FLDO_ID", as_index=False)
    .first()
)

pga = pga[
    [
        "FLDO_ID",
        "GMIM_VALUE_NUM",
    ]
].rename(
    columns={
        "GMIM_VALUE_NUM": "PGA_g"
    }
)

print(
    f"PGA-linked observations: "
    f"{len(pga)}"
)


# ================================================================
# 12. PGV
# ================================================================

print("\nProcessing PGV...")

pgv = gmim[
    gmim["GMIM_TYPE_CLEAN"] == "PGV"
].copy()

pgv = pgv[
    pgv["GMIM_UNIT_CLEAN"].str.lower() == "m/s"
].copy()

pgv["component_priority"] = (
    pgv["GMIM_COMP_CLEAN"]
    .str.upper()
    .map(
        {
            "ROTD50": 1,
            "GEOMEAN": 2,
            "MAX": 3,
            "H1": 4,
            "H2": 5,
        }
    )
    .fillna(99)
)

pgv = pgv.sort_values(
    [
        "FLDO_ID",
        "component_priority",
    ]
)

pgv = (
    pgv
    .groupby("FLDO_ID", as_index=False)
    .first()
)

pgv = pgv[
    [
        "FLDO_ID",
        "GMIM_VALUE_NUM",
    ]
].rename(
    columns={
        "GMIM_VALUE_NUM": "PGV_mps"
    }
)

print(
    f"PGV-linked observations: "
    f"{len(pgv)}"
)


# ================================================================
# 13. ARIAS INTENSITY
# ================================================================

print("\nProcessing Arias Intensity...")

arias = gmim[
    gmim["GMIM_TYPE_CLEAN"] == "ARIAS INTENSITY"
].copy()

arias = arias[
    arias["GMIM_UNIT_CLEAN"].str.lower() == "m/s"
].copy()

arias["component_priority"] = (
    arias["GMIM_COMP_CLEAN"]
    .str.upper()
    .map(
        {
            "ROTD50": 1,
            "GEOMEAN": 2,
            "MAX": 3,
            "H1": 4,
            "H2": 5,
        }
    )
    .fillna(99)
)

arias = arias.sort_values(
    [
        "FLDO_ID",
        "component_priority",
    ]
)

arias = (
    arias
    .groupby("FLDO_ID", as_index=False)
    .first()
)

arias = arias[
    [
        "FLDO_ID",
        "GMIM_VALUE_NUM",
    ]
].rename(
    columns={
        "GMIM_VALUE_NUM": "Arias_Intensity"
    }
)

print(
    f"Arias-linked observations: "
    f"{len(arias)}"
)


# ================================================================
# 14. MERGE GROUND-MOTION FEATURES
# ================================================================

clean = clean.merge(
    pga,
    on="FLDO_ID",
    how="left",
    validate="one_to_one",
)

clean = clean.merge(
    pgv,
    on="FLDO_ID",
    how="left",
    validate="one_to_one",
)

clean = clean.merge(
    arias,
    on="FLDO_ID",
    how="left",
    validate="one_to_one",
)


# ================================================================
# 15. GROUND-MOTION COVERAGE
# ================================================================

print("\n" + "=" * 70)
print("GROUND-MOTION COVERAGE")
print("=" * 70)

for feature in [
    "PGA_g",
    "PGV_mps",
    "Arias_Intensity",
]:

    count = clean[feature].notna().sum()

    print(
        f"{feature:20s}: "
        f"{count}/{len(clean)} "
        f"({100 * count / len(clean):.2f}%)"
    )


# ================================================================
# 16. EVENT MAGNITUDE
# ================================================================

clean["magnitude"] = numeric(
    clean["EVNT_MAG"]
)

print("\nMagnitude coverage:")

count = clean["magnitude"].notna().sum()

print(
    f"{count}/{len(clean)} "
    f"({100 * count / len(clean):.2f}%)"
)


# ================================================================
# 17. FINAL MODEL DATASET
# ================================================================

model_columns = [
    "FLDO_ID",
    "EVNT_ID",
    "SITE_ID",
    "EVNT_NM",
    "EVNT_YR",
    "SITE_NAME",
    "latitude",
    "longitude",
    "magnitude",
    "PGA_g",
    "PGV_mps",
    "Arias_Intensity",
    "lateral_spreading",
]

model_columns = [
    c for c in model_columns
    if c in clean.columns
]

final = clean[model_columns].copy()


# ================================================================
# 18. REMOVE ROWS WITHOUT PRIMARY PGA
# ================================================================

before_pga = len(final)

final = final[
    final["PGA_g"].notna()
].copy()

print("\n" + "=" * 70)
print("PGA REQUIREMENT")
print("=" * 70)

print(
    f"Rows before PGA requirement: {before_pga}"
)

print(
    f"Rows after PGA requirement:  {len(final)}"
)


# ================================================================
# 19. DUPLICATE CHECK
# ================================================================

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

print(
    "Duplicate FLDO_ID:",
    final["FLDO_ID"].duplicated().sum()
)

print(
    "Duplicate EVNT_ID + FLDO_ID:",
    final.duplicated(
        ["EVNT_ID", "FLDO_ID"]
    ).sum()
)


# ================================================================
# 20. FINAL LABEL BALANCE
# ================================================================

print("\n" + "=" * 70)
print("FINAL LABEL BALANCE")
print("=" * 70)

print(
    final["lateral_spreading"]
    .value_counts()
    .sort_index()
)

positive = (
    final["lateral_spreading"] == 1
).sum()

negative = (
    final["lateral_spreading"] == 0
).sum()

print(
    f"\nPositive: {positive}"
)

print(
    f"Negative: {negative}"
)

if len(final) > 0:
    print(
        f"Positive percentage: "
        f"{100 * positive / len(final):.2f}%"
    )


# ================================================================
# 21. EVENT SUMMARY
# ================================================================

event_summary = (
    final
    .groupby(
        [
            "EVNT_ID",
            "EVNT_NM",
            "EVNT_YR",
            "magnitude",
        ],
        dropna=False,
    )
    .agg(
        observations=(
            "FLDO_ID",
            "nunique",
        ),
        positive_observations=(
            "lateral_spreading",
            "sum",
        ),
        sites=(
            "SITE_ID",
            "nunique",
        ),
        pga_mean=(
            "PGA_g",
            "mean",
        ),
        pga_min=(
            "PGA_g",
            "min",
        ),
        pga_max=(
            "PGA_g",
            "max",
        ),
    )
    .reset_index()
)

event_summary["negative_observations"] = (
    event_summary["observations"]
    - event_summary["positive_observations"]
)

event_summary["has_positive"] = (
    event_summary["positive_observations"] > 0
)

event_summary["has_negative"] = (
    event_summary["negative_observations"] > 0
)

event_summary["mixed"] = (
    event_summary["has_positive"]
    &
    event_summary["has_negative"]
)


# ================================================================
# 22. EVENT AUDIT
# ================================================================

print("\n" + "=" * 70)
print("FINAL EVENT AUDIT")
print("=" * 70)

print(
    f"Events: "
    f"{len(event_summary)}"
)

print(
    f"Positive events: "
    f"{event_summary['has_positive'].sum()}"
)

print(
    f"Negative events: "
    f"{event_summary['has_negative'].sum()}"
)

print(
    f"Mixed events: "
    f"{event_summary['mixed'].sum()}"
)

print(
    f"Events with only positive observations: "
    f"{((event_summary['has_positive']) & (~event_summary['has_negative'])).sum()}"
)

print(
    f"Events with only negative observations: "
    f"{((event_summary['has_negative']) & (~event_summary['has_positive'])).sum()}"
)


# ================================================================
# 23. EVENT SAMPLE DISTRIBUTION
# ================================================================

print("\nObservations per event:")
print(
    event_summary[
        [
            "EVNT_ID",
            "EVNT_NM",
            "observations",
            "positive_observations",
            "negative_observations",
            "mixed",
        ]
    ]
    .sort_values(
        "observations",
        ascending=False,
    )
    .to_string(index=False)
)


# ================================================================
# 24. SAVE
# ================================================================

final = final.sort_values(
    [
        "EVNT_ID",
        "SITE_ID",
        "FLDO_ID",
    ]
).reset_index(drop=True)

final.to_csv(
    OUTPUT_FILE,
    index=False,
)

event_summary.to_csv(
    EVENT_OUTPUT,
    index=False,
)


# ================================================================
# 25. FINAL SAFETY CHECK
# ================================================================

forbidden = [
    "FLDM_LTSP",
    "FLDM_DESC",
    "FLDM_SFEV",
    "FLDM_SNBL",
    "FLDM_STTL",
    "FLDM_STDM",
    "FLDM_GMFR",
    "FLDD_HDIS",
    "FLDD_VDIS",
    "FLDD_AZIM",
]

forbidden_present = [
    c for c in forbidden
    if c in final.columns
]

print("\n" + "=" * 70)
print("FINAL LEAKAGE CHECK")
print("=" * 70)

print(
    "Forbidden columns in model dataset:",
    forbidden_present
)

print(
    "\nModel features:"
)

for feature in [
    "PGA_g",
    "PGV_mps",
    "Arias_Intensity",
]:
    if feature in final.columns:
        print(f"[FEATURE] {feature}")

print("\nTarget:")
print("[TARGET]  lateral_spreading")

print("\nLOEO grouping:")
print("[GROUP]   EVNT_ID")


# ================================================================
# 26. FINAL MESSAGE
# ================================================================

print("\n" + "=" * 70)
print("P4 CLEAN DATASET COMPLETE")
print("=" * 70)

print(
    f"\nFinal dataset: {OUTPUT_FILE}"
)

print(
    f"Final rows: {len(final)}"
)

print(
    f"Final events: {final['EVNT_ID'].nunique()}"
)

print(
    f"Final sites: {final['SITE_ID'].nunique()}"
)

print(
    "\nNO P4 MODEL WAS TRAINED."
)

print(
    "NO EXISTING QUAKESHIELD MODEL WAS MODIFIED."
)

print(
    "\nNext step: inspect this dataset before P4 training."
)