import pandas as pd

df = pd.read_csv("p1_prediction_outputs.csv")

events = (
    df.groupby(
        ["earthquake_id", "earthquake_name", "earthquake_date"]
    )
    .agg(
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        mean_p1_probability=("P1_ground_failure_probability", "mean"),
        max_p1_probability=("P1_ground_failure_probability", "max"),
        locations=("P1_ground_failure_probability", "count")
    )
    .reset_index()
)

print("=" * 80)
print("QUAKESHIELD P1 EARTHQUAKE EVENTS")
print("=" * 80)

print(events.to_string(index=False))
