import os
import pandas as pd
import numpy as np

BASE = "outputs"

FLDO_FILE = os.path.join(BASE, "ngl_field_observations.csv")
FLDM_FILE = os.path.join(BASE, "ngl_liquefaction_manifestations.csv")
SITES_FILE = os.path.join(BASE, "ngl_sites.csv")
EVENTS_FILE = os.path.join(BASE, "ngl_events.csv")
GMIM_FILE = os.path.join(BASE, "ngl_ground_motion.csv")


def clean_id(series):
    return pd.to_numeric(series, errors="coerce").astype("Int64")


print("=" * 70)
print("QUAKESHIELD — NGL P4 EVENT-LEVEL AUDIT")
print("=" * 70)

# -------------------------------------------------------------------
# LOAD
# -------------------------------------------------------------------

print("\nLoading NGL files...")

fldo = pd.read_csv(FLDO_FILE)
fldm = pd.read_csv(FLDM_FILE)
sites = pd.read_csv(SITES_FILE)
events = pd.read_csv(EVENTS_FILE)
gmim = pd.read_csv(GMIM_FILE)

print(f"Field observations: {len(fldo)}")
print(f"Manifestations:      {len(fldm)}")
print(f"Sites:               {len(sites)}")
print(f"Events:              {len(events)}")
print(f"Ground motion:       {len(gmim)}")


# -------------------------------------------------------------------
# NORMALIZE IDS
# -------------------------------------------------------------------

for df in [fldo, fldm, gmim]:
    if "FLDO_ID" in df.columns:
        df["FLDO_ID"] = clean_id(df["FLDO_ID"])

fldo["EVNT_ID"] = clean_id(fldo["EVNT_ID"])
fldo["SITE_ID"] = clean_id(fldo["SITE_ID"])

if "SITE_ID" in sites.columns:
    sites["SITE_ID"] = clean_id(sites["SITE_ID"])

if "EVNT_ID" in events.columns:
    events["EVNT_ID"] = clean_id(events["EVNT_ID"])


# -------------------------------------------------------------------
# FILTER USABLE LABELS
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("USABLE LABELS")
print("=" * 70)

usable = fldm[fldm["FLDM_LTSP"].isin([0, 1])].copy()

print(f"Usable manifestations: {len(usable)}")
print(f"  Negative (0): {(usable['FLDM_LTSP'] == 0).sum()}")
print(f"  Positive (1): {(usable['FLDM_LTSP'] == 1).sum()}")
print(f"  Excluded LTSP=2: {(fldm['FLDM_LTSP'] == 2).sum()}")


# -------------------------------------------------------------------
# LINK MANIFESTATIONS -> FIELD OBSERVATIONS
# -------------------------------------------------------------------

merged = usable.merge(
    fldo[
        [
            "FLDO_ID",
            "EVNT_ID",
            "SITE_ID",
            "FLDO_DESC",
            "FLDO_STAT",
            "FLDO_REVW",
        ]
    ],
    on="FLDO_ID",
    how="left",
    validate="many_to_one",
)

print("\nObservation linkage")
print("-" * 70)

print(f"Manifestations linked to FLDO: {merged['EVNT_ID'].notna().sum()}")
print(f"Manifestations missing FLDO linkage: {merged['EVNT_ID'].isna().sum()}")
print(f"Unique field observations: {merged['FLDO_ID'].nunique()}")


# -------------------------------------------------------------------
# EVENT-LEVEL ANALYSIS
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("EVENT-LEVEL ANALYSIS")
print("=" * 70)

event_summary = (
    merged.dropna(subset=["EVNT_ID"])
    .groupby("EVNT_ID")
    .agg(
        manifestation_count=("FLDM_ID", "count"),
        positive_count=("FLDM_LTSP", "sum"),
        negative_count=("FLDM_LTSP", lambda x: (x == 0).sum()),
        observation_count=("FLDO_ID", "nunique"),
        site_count=("SITE_ID", "nunique"),
    )
    .reset_index()
)

event_summary["has_positive"] = event_summary["positive_count"] > 0
event_summary["has_negative"] = event_summary["negative_count"] > 0
event_summary["has_both"] = (
    event_summary["has_positive"]
    & event_summary["has_negative"]
)

print(f"Events with usable manifestations: {len(event_summary)}")
print(
    f"Events with positive LTSP: "
    f"{event_summary['has_positive'].sum()}"
)
print(
    f"Events with negative LTSP: "
    f"{event_summary['has_negative'].sum()}"
)
print(
    f"Events containing BOTH positive and negative: "
    f"{event_summary['has_both'].sum()}"
)


# -------------------------------------------------------------------
# EVENT DETAILS
# -------------------------------------------------------------------

event_details = event_summary.merge(
    events,
    on="EVNT_ID",
    how="left",
    suffixes=("", "_EVENT"),
)

event_details = event_details.sort_values(
    ["positive_count", "manifestation_count"],
    ascending=False,
)

event_details.to_csv(
    os.path.join(BASE, "ngl_lateral_spread_event_summary.csv"),
    index=False,
)

print("\nSaved:")
print("outputs\\ngl_lateral_spread_event_summary.csv")


# -------------------------------------------------------------------
# PRINT EVENT SUMMARY
# -------------------------------------------------------------------

display_columns = [
    c
    for c in [
        "EVNT_ID",
        "EVNT_NM",
        "EVNT_YR",
        "EVNT_MAG",
        "manifestation_count",
        "positive_count",
        "negative_count",
        "observation_count",
        "site_count",
        "has_both",
    ]
    if c in event_details.columns
]

print("\nEvent summary:")
print(
    event_details[display_columns]
    .to_string(index=False)
)


# -------------------------------------------------------------------
# SITE-LEVEL ANALYSIS
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("SITE-LEVEL ANALYSIS")
print("=" * 70)

site_summary = (
    merged.dropna(subset=["SITE_ID"])
    .groupby("SITE_ID")
    .agg(
        manifestation_count=("FLDM_ID", "count"),
        positive_count=("FLDM_LTSP", "sum"),
        negative_count=("FLDM_LTSP", lambda x: (x == 0).sum()),
        observation_count=("FLDO_ID", "nunique"),
        event_count=("EVNT_ID", "nunique"),
    )
    .reset_index()
)

site_summary["has_positive"] = site_summary["positive_count"] > 0
site_summary["has_negative"] = site_summary["negative_count"] > 0
site_summary["has_both"] = (
    site_summary["has_positive"]
    & site_summary["has_negative"]
)

print(f"Sites with usable manifestations: {len(site_summary)}")
print(
    f"Sites with positive LTSP: "
    f"{site_summary['has_positive'].sum()}"
)
print(
    f"Sites with negative LTSP: "
    f"{site_summary['has_negative'].sum()}"
)
print(
    f"Sites containing BOTH positive and negative: "
    f"{site_summary['has_both'].sum()}"
)

site_details = site_summary.merge(
    sites,
    on="SITE_ID",
    how="left",
    suffixes=("", "_SITE"),
)

site_details.to_csv(
    os.path.join(BASE, "ngl_lateral_spread_site_summary.csv"),
    index=False,
)

print("\nSaved:")
print("outputs\\ngl_lateral_spread_site_summary.csv")


# -------------------------------------------------------------------
# EVENT CLASS BALANCE
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("EVENT CLASS BALANCE")
print("=" * 70)

positive_events = event_summary[
    event_summary["has_positive"]
]

negative_events = event_summary[
    event_summary["has_negative"]
]

both_events = event_summary[
    event_summary["has_both"]
]

print(
    f"Positive-event count: {len(positive_events)}"
)

print(
    f"Negative-event count: {len(negative_events)}"
)

print(
    f"Mixed-event count:    {len(both_events)}"
)


# -------------------------------------------------------------------
# SINGLE-CLASS EVENTS
# -------------------------------------------------------------------

print("\nEvents with ONLY positive observations:")
print("-" * 70)

only_positive = event_summary[
    event_summary["has_positive"]
    & ~event_summary["has_negative"]
].sort_values(
    "positive_count",
    ascending=False,
)

print(
    only_positive[
        [
            "EVNT_ID",
            "manifestation_count",
            "positive_count",
            "negative_count",
            "observation_count",
            "site_count",
        ]
    ].to_string(index=False)
)

print("\nEvents with ONLY negative observations:")
print("-" * 70)

only_negative = event_summary[
    ~event_summary["has_positive"]
    & event_summary["has_negative"]
].sort_values(
    "negative_count",
    ascending=False,
)

print(
    only_negative[
        [
            "EVNT_ID",
            "manifestation_count",
            "positive_count",
            "negative_count",
            "observation_count",
            "site_count",
        ]
    ].to_string(index=False)
)


# -------------------------------------------------------------------
# GROUND MOTION AVAILABILITY BY EVENT
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("GROUND-MOTION AVAILABILITY")
print("=" * 70)

gmim_obs = set(
    gmim["FLDO_ID"]
    .dropna()
    .astype(int)
)

event_gmim = (
    merged.dropna(subset=["EVNT_ID"])
    .groupby("EVNT_ID")
    .agg(
        observations=("FLDO_ID", "nunique"),
        positive_observations=(
            "FLDO_ID",
            lambda x: x.isin(
                merged.loc[
                    merged["FLDM_LTSP"] == 1,
                    "FLDO_ID"
                ].unique()
            ).sum(),
        ),
    )
    .reset_index()
)

event_gmim["gmim_linked_observations"] = (
    event_gmim["EVNT_ID"]
    .map(
        merged[
            merged["FLDO_ID"].isin(gmim_obs)
        ]
        .groupby("EVNT_ID")["FLDO_ID"]
        .nunique()
    )
    .fillna(0)
    .astype(int)
)

event_gmim["has_ground_motion"] = (
    event_gmim["gmim_linked_observations"] > 0
)

print(
    f"Events with ground-motion-linked observations: "
    f"{event_gmim['has_ground_motion'].sum()}"
)

print(
    f"Events without linked ground-motion observations: "
    f"{(~event_gmim['has_ground_motion']).sum()}"
)


# -------------------------------------------------------------------
# PGA COVERAGE
# -------------------------------------------------------------------

pga = gmim[
    gmim["GMIM_TYPE"]
    .astype(str)
    .str.upper()
    .eq("PGA")
].copy()

print("\nPGA records:")
print(f"Total PGA records: {len(pga)}")
print(
    f"PGA-linked observations: "
    f"{pga['FLDO_ID'].nunique()}"
)


# -------------------------------------------------------------------
# FINAL TRAINABILITY CHECK
# -------------------------------------------------------------------

print("\n" + "=" * 70)
print("P4 TRAINABILITY CHECK")
print("=" * 70)

usable_events = len(event_summary)
positive_event_count = len(positive_events)
negative_event_count = len(negative_events)
mixed_event_count = len(both_events)

print(f"Usable events: {usable_events}")
print(f"Positive events: {positive_event_count}")
print(f"Negative events: {negative_event_count}")
print(f"Mixed events: {mixed_event_count}")

print("\nPreliminary rule:")
print(
    "Need multiple independent positive and negative earthquake "
    "events before event-held-out model training."
)

if positive_event_count >= 5 and negative_event_count >= 5:
    print(
        "\nPRELIMINARY VERDICT: GREEN"
    )
    print(
        "There appear to be enough event groups for further "
        "P4 dataset construction and LOEO validation."
    )
else:
    print(
        "\nPRELIMINARY VERDICT: RED/CAUTION"
    )
    print(
        "Event-level diversity is insufficient for a defensible "
        "P4 predictive model at this stage."
    )

print("\nIMPORTANT:")
print(
    "This script does NOT train a model."
)
print(
    "Displacement variables are NOT used as predictors."
)
print(
    "FLDM_LTSP=2 is excluded."
)

print("\n" + "=" * 70)
print("P4 EVENT AUDIT COMPLETE")
print("=" * 70)