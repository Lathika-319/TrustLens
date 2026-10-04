import sys
import json
import pandas as pd

df = pd.read_csv(sys.argv[1])

print("Columns:", list(df.columns))


def col(*names):
    for n in names:
        if n in df.columns:
            return n
    return None


m = {
    "location": col("location_name", "location"),
    "date": col("earthquake_date", "date"),
    "lat": col("latitude", "scenario_latitude"),
    "lon": col("longitude", "scenario_longitude"),
    "magnitude": col("magnitude"),
    "groundFailure": col("P1_ground_failure_score"),
    "liquefaction": col("mean_P2_liquefaction_probability"),
    "score": col("final_risk_score"),
    "risk": col("risk_level"),
    "priority": col("priority_level"),
    "hospitalKm": col("nearest_hospital_km"),
    "schoolKm": col("nearest_school_km"),
    "bridgeKm": col("nearest_bridge_km"),
    "roadKm": col("nearest_road_km"),
}


for k, v in m.items():
    print(f"  {k:14s} <- {v}")


required = [
    "location",
    "date",
    "lat",
    "lon",
    "magnitude",
    "groundFailure",
    "liquefaction",
    "score",
    "risk",
    "priority",
]

missing = [k for k in required if m[k] is None]

if missing:
    raise ValueError(f"Missing required fields: {missing}")


out = pd.DataFrame({
    k: df[v]
    for k, v in m.items()
    if v is not None
})


# Keep the exact scenario names from the verified active output.
# Do NOT shorten or rewrite location names.


def clean_priority(value):
    value = str(value)

    if value == "PRIORITIZE - INFRASTRUCTURE NEARBY":
        return "Review: mapped infrastructure nearby"

    if value == "MONITOR / FURTHER ASSESSMENT":
        return "Review: further assessment"

    if value == "LOWER PRIORITY":
        return "Lower review priority"

    return value


out["priority"] = out["priority"].apply(clean_priority)


def format_distance(value):
    if pd.isna(value):
        return "No mapped feature"

    return f"{float(value):.2f} km"


def make_explanation(row):
    hospital = format_distance(row.get("hospitalKm"))
    school = format_distance(row.get("schoolKm"))
    bridge = format_distance(row.get("bridgeKm"))
    road = format_distance(row.get("roadKm"))

    return (
        f"Ground-failure model score is {float(row['groundFailure']):.3f}, "
        f"while the matched liquefaction model score is "
        f"{float(row['liquefaction']):.3f}. "
        f"The heuristic combined hazard model indicator is "
        f"{float(row['score']):.3f}. "
        f"Score band: {row['risk']}. "
        f"Mapped infrastructure proximity context: "
        f"hospital {hospital}; school {school}; "
        f"bridge {bridge}; major road {road}. "
        f"Review cue: {row['priority']}."
    )


out["explanation"] = out.apply(make_explanation, axis=1)


out = out.round(6)


print()
print("Generated scenario records:")
print(
    out[
        [
            "location",
            "groundFailure",
            "liquefaction",
            "score",
            "risk",
            "priority",
        ]
    ].to_string(index=False)
)


with open("src/scenarioData.js", "w", encoding="utf-8") as f:
    f.write(
        "export const scenarioData = "
        + json.dumps(
            json.loads(out.to_json(orient="records")),
            indent=2
        )
        + ";\n"
    )


print()
print("Wrote src/scenarioData.js:", len(out), "records")
