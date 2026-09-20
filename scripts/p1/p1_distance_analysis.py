import pandas as pd

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

for event, group in df.groupby("earthquake_id"):

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("=" * 70)

    result = group.groupby("label")[
        "distance_to_epicenter_km"
    ].agg([
        "count",
        "mean",
        "median",
        "min",
        "max"
    ])

    result.index = result.index.map({
        0: "background",
        1: "landslide"
    })

    print(result.round(3))
