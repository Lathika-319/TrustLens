import sys, json
import pandas as pd

df = pd.read_csv(sys.argv[1])
print("Columns:", list(df.columns))

def col(*names):
    for n in names:
        if n in df.columns:
            return n

m = {
    "location": col("location_name", "location"),
    "date": col("earthquake_date", "date"),
    "lat": col("latitude", "scenario_latitude"),
    "lon": col("longitude", "scenario_longitude"),
    "magnitude": col("magnitude"),
    "groundFailure": col("P1_ground_failure_probability"),
    "liquefaction": col("mean_P2_liquefaction_probability"),
    "score": col("final_risk_score"),
    "risk": col("risk_level"),
    "priority": col("priority_level"),
    "explanation": col("explanation", "risk_explanation"),
    "hospitalKm": col("nearest_hospital_km"),
    "schoolKm": col("nearest_school_km"),
    "bridgeKm": col("nearest_bridge_km"),
    "roadKm": col("nearest_road_km"),
}
for k, v in m.items():
    print(f"  {k:14s} <- {v}")

out = pd.DataFrame({k: df[v] for k, v in m.items() if v})
out["location"] = (out["location"].astype(str)
    .str.replace(r"^M [\d.]+ - ", "", regex=True)
    .str.replace(r"^\d+ ?km [NSEW]+ of ", "", regex=True))
for c in ("priority", "explanation"):
    if c in out:
        out[c] = out[c].astype(str).str.replace(
            "INFRASTRUCTURE AT RISK", "INFRASTRUCTURE NEARBY", regex=False)
out = out.round(6)

print(out.drop(columns=["explanation"], errors="ignore").to_string())
with open("src/scenarioData.js", "w", encoding="utf-8") as f:
    f.write("export const scenarioData = " + json.dumps(json.loads(out.to_json(orient="records")), indent=2) + ";\n")
print("Wrote src/scenarioData.js:", len(out), "records")
