import os
import numpy as np
import pandas as pd


# ============================================================
# QUAKE SHIELD - INFRASTRUCTURE PROXIMITY
# ============================================================

INPUT_FILE = r"outputs\infrastructure_data.csv"
SCENARIO_FILE = r"outputs\quakeshield_map_data.csv"
OUTPUT_FILE = r"outputs\infrastructure_risk.csv"


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate straight-line distance between
    two geographic coordinates in kilometres.
    """

    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return earth_radius * c


# ============================================================
# LOAD DATA
# ============================================================

infrastructure = pd.read_csv(
    INPUT_FILE
)

scenarios = pd.read_csv(
    SCENARIO_FILE
)


print(
    f"Infrastructure records: "
    f"{len(infrastructure)}"
)

print(
    f"Risk scenarios: "
    f"{len(scenarios)}"
)


# ============================================================
# CLEAN COORDINATES
# ============================================================

coordinate_columns = [
    "scenario_latitude",
    "scenario_longitude",
    "infra_latitude",
    "infra_longitude"
]

for column in coordinate_columns:

    infrastructure[column] = pd.to_numeric(
        infrastructure[column],
        errors="coerce"
    )


infrastructure = infrastructure.dropna(
    subset=[
        "scenario_latitude",
        "scenario_longitude",
        "infra_latitude",
        "infra_longitude"
    ]
)


# ============================================================
# INFRASTRUCTURE CATEGORIES
# ============================================================

hospital_types = {
    "hospital"
}

school_types = {
    "school"
}

bridge_types = {
    "bridge"
}

road_types = {
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary"
}


# ============================================================
# FIND NEAREST INFRASTRUCTURE
# ============================================================

results = []


for _, scenario in scenarios.iterrows():

    earthquake_id = scenario[
        "earthquake_id"
    ]

    location_name = scenario[
        "location_name"
    ]

    scenario_lat = scenario[
        "latitude"
    ]

    scenario_lon = scenario[
        "longitude"
    ]


    scenario_data = infrastructure[
        infrastructure["earthquake_id"]
        == earthquake_id
    ].copy()


    result = {
        "earthquake_id":
            earthquake_id,

        "location_name":
            location_name,

        "nearby_hospital":
            0,

        "nearby_school":
            0,

        "nearby_bridge":
            0,

        "nearby_road":
            0,

        "nearest_hospital_km":
            np.nan,

        "nearest_school_km":
            np.nan,

        "nearest_bridge_km":
            np.nan,

        "nearest_road_km":
            np.nan
    }


    if len(scenario_data) == 0:

        results.append(result)

        continue


    # --------------------------------------------------------
    # Calculate distance for every infrastructure feature
    # --------------------------------------------------------

    scenario_data["distance_km"] = haversine_distance(
        scenario_lat,
        scenario_lon,
        scenario_data["infra_latitude"].values,
        scenario_data["infra_longitude"].values
    )


    # --------------------------------------------------------
    # Normalize infrastructure type
    # --------------------------------------------------------

    scenario_data[
        "infrastructure_type"
    ] = (
        scenario_data[
            "infrastructure_type"
        ]
        .astype(str)
        .str.lower()
    )


    # --------------------------------------------------------
    # Hospital
    # --------------------------------------------------------

    hospitals = scenario_data[
        scenario_data[
            "infrastructure_type"
        ].isin(hospital_types)
    ]

    if len(hospitals) > 0:

        result[
            "nearby_hospital"
        ] = 1

        result[
            "nearest_hospital_km"
        ] = hospitals[
            "distance_km"
        ].min()


    # --------------------------------------------------------
    # School
    # --------------------------------------------------------

    schools = scenario_data[
        scenario_data[
            "infrastructure_type"
        ].isin(school_types)
    ]

    if len(schools) > 0:

        result[
            "nearby_school"
        ] = 1

        result[
            "nearest_school_km"
        ] = schools[
            "distance_km"
        ].min()


    # --------------------------------------------------------
    # Bridge
    # --------------------------------------------------------

    bridges = scenario_data[
        scenario_data[
            "infrastructure_type"
        ].isin(bridge_types)
    ]

    if len(bridges) > 0:

        result[
            "nearby_bridge"
        ] = 1

        result[
            "nearest_bridge_km"
        ] = bridges[
            "distance_km"
        ].min()


    # --------------------------------------------------------
    # Major road
    # --------------------------------------------------------

    roads = scenario_data[
        scenario_data[
            "infrastructure_type"
        ].isin(road_types)
    ]

    if len(roads) > 0:

        result[
            "nearby_road"
        ] = 1

        result[
            "nearest_road_km"
        ] = roads[
            "distance_km"
        ].min()


    results.append(result)


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

risk_df = pd.DataFrame(
    results
)


# ============================================================
# INFRASTRUCTURE COUNT
# ============================================================

risk_df[
    "infrastructure_count"
] = (
    risk_df["nearby_hospital"]
    + risk_df["nearby_school"]
    + risk_df["nearby_bridge"]
    + risk_df["nearby_road"]
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "outputs",
    exist_ok=True
)

risk_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 75)
print(
    "INFRASTRUCTURE PROXIMITY ANALYSIS COMPLETED"
)
print("=" * 75)


display_columns = [
    "earthquake_id",
    "location_name",
    "nearest_hospital_km",
    "nearest_school_km",
    "nearest_bridge_km",
    "nearest_road_km",
    "infrastructure_count"
]


print(
    risk_df[
        display_columns
    ].to_string(index=False)
)


print("\nSaved:")
print(OUTPUT_FILE)