import pandas as pd
import numpy as np

ANCHOR_PGA = r"outputs\verified_ngl_anchor_pga_direct.csv"
DATABASE = r"data\raw\Database 7.xlsx"
OUT = r"outputs\verified_ngl_anchor_evidence.csv"


anchors = pd.read_csv(ANCHOR_PGA)

db = pd.read_excel(
    DATABASE,
    sheet_name="Liq database",
)

db["Country"] = db["Country"].astype(str).str.strip()
db["Reference"] = db["Reference"].astype(str).str.strip()
db["Site"] = db["Site"].astype(str).str.strip()

kayen = db[
    (db["Reference"] == "Kayen et al. (2013)")
    & (db["Country"] == "Japan")
].copy()


groups = {
    "Kobe|Port Island": kayen[
        kayen["Site"].str.contains(
            "Port Island",
            case=False,
            na=False,
        )
    ],

    "Kobe|Nishinomiya": kayen[
        kayen["Site"].str.contains(
            "Nishinomiya",
            case=False,
            na=False,
        )
    ],

    "Niigata-Chuetsu|Kawagishi-cho": kayen[
        kayen["Site"].str.contains(
            "Kawagishi",
            case=False,
            na=False,
        )
    ],

    "Niigata-Chuetsu|Showa Bridge": kayen[
        kayen["Site"].str.contains(
            "Showa Bridge",
            case=False,
            na=False,
        )
    ],

    "Tohoku-Oki|Arahama": kayen[
        kayen["Site"].str.contains(
            "Arahama",
            case=False,
            na=False,
        )
    ],

    "Tohoku-Oki|Yuriage": kayen[
        kayen["Site"].str.contains(
            "Yuriage",
            case=False,
            na=False,
        )
    ],

    "Tohoku-Oki|Aomori": kayen[
        kayen["Site"].str.contains(
            "Aomori",
            case=False,
            na=False,
        )
    ],

    "Tohoku-Oki|Takeda": kayen[
        kayen["Site"].str.contains(
            "Takeda Elementary",
            case=False,
            na=False,
        )
    ],
}


summary_rows = []

for key, df in groups.items():

    scenario, anchor_group = key.split("|")

    summary_rows.append(
        {
            "scenario": scenario,
            "anchor_group": anchor_group,
            "historical_records": len(df),
            "historical_unique_sites": df["Site"].nunique(),
            "historical_L_rate": (
                df["L"].mean()
                if len(df)
                else np.nan
            ),
            "historical_PGA_mean": (
                df["PGA(g)"].mean()
                if len(df)
                else np.nan
            ),
            "historical_PGA_min": (
                df["PGA(g)"].min()
                if len(df)
                else np.nan
            ),
            "historical_PGA_max": (
                df["PGA(g)"].max()
                if len(df)
                else np.nan
            ),
            "historical_Mw_min": (
                df["Mw"].min()
                if len(df)
                else np.nan
            ),
            "historical_Mw_max": (
                df["Mw"].max()
                if len(df)
                else np.nan
            ),
        }
    )


historical = pd.DataFrame(summary_rows)

anchors["ShakeMap_PGA_g"] = np.exp(
    anchors["shakemap_pga_raw"]
)

result = anchors.merge(
    historical,
    on=["scenario", "anchor_group"],
    how="left",
)


columns = [
    "scenario",
    "anchor_group",
    "ngl_site",
    "match_level",
    "anchor_latitude",
    "anchor_longitude",
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
]


print("\n================================")
print("VERIFIED ANCHOR EVIDENCE")
print("================================")

print(
    result[columns].to_string(
        index=False
    )
)


result.to_csv(
    OUT,
    index=False,
)

print("\nSaved:", OUT)