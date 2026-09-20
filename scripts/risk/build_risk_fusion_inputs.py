import pandas as pd

# Load P1 predictions
p1 = pd.read_csv("p1_prediction_outputs.csv")

# Load P2 risk layer
p2 = pd.read_csv("p2_risk_layer.csv")

# --------------------------------------------------
# P1: summarize each earthquake scenario
# --------------------------------------------------

p1_events = (
    p1.groupby(
        [
            "earthquake_id",
            "earthquake_name",
            "earthquake_date"
        ]
    )
    .agg(
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        earthquake_magnitude=("earthquake_id", "size"),
        P1_ground_failure_probability=(
            "P1_ground_failure_probability",
            "mean"
        )
    )
    .reset_index()
)

# Get actual magnitude from original P1 dataset
p1_original = pd.read_csv(
    r"data\raw\QuakeShield_Final_Dataset.csv"
)

event_magnitude = (
    p1_original
    .groupby("earthquake_id")["earthquake_magnitude"]
    .first()
    .reset_index()
)

p1_events = p1_events.drop(
    columns=["earthquake_magnitude"]
)

p1_events = p1_events.merge(
    event_magnitude,
    on="earthquake_id",
    how="left"
)

# --------------------------------------------------
# P2: summarize liquefaction susceptibility
# by Mw scenario
# --------------------------------------------------

p2_summary = (
    p2.groupby("Mw")
    .agg(
        mean_P2_liquefaction_probability=(
            "P2_liquefaction_probability",
            "mean"
        ),
        max_P2_liquefaction_probability=(
            "P2_liquefaction_probability",
            "max"
        ),
        number_of_sites=(
            "P2_liquefaction_probability",
            "count"
        )
    )
    .reset_index()
)

# --------------------------------------------------
# Match each P1 earthquake to the nearest available
# Mw value in the P2 database.
# --------------------------------------------------

def nearest_mw(magnitude):
    differences = abs(
        p2_summary["Mw"] - magnitude
    )
    return p2_summary.loc[
        differences.idxmin(), "Mw"
    ]

p1_events["matched_P2_Mw"] = (
    p1_events["earthquake_magnitude"]
    .apply(nearest_mw)
)

fusion_inputs = p1_events.merge(
    p2_summary,
    left_on="matched_P2_Mw",
    right_on="Mw",
    how="left"
)

fusion_inputs = fusion_inputs[
    [
        "earthquake_id",
        "earthquake_name",
        "earthquake_date",
        "latitude",
        "longitude",
        "earthquake_magnitude",
        "P1_ground_failure_probability",
        "matched_P2_Mw",
        "mean_P2_liquefaction_probability",
        "max_P2_liquefaction_probability",
        "number_of_sites"
    ]
]

# Save
output_file = "risk_fusion_inputs.csv"

fusion_inputs.to_csv(
    output_file,
    index=False
)

print("=" * 70)
print("QUAKESHIELD RISK FUSION INPUTS CREATED")
print("=" * 70)

print("\nEarthquake scenarios:", len(fusion_inputs))

print("\nFusion inputs:")
print(fusion_inputs.to_string(index=False))

print("\nSaved:")
print(output_file)
