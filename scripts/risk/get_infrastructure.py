import os
import pandas as pd
import osmnx as ox


# ============================================================
# QUAKESHIELD - INFRASTRUCTURE COLLECTION
# ============================================================

INPUT_FILE = r"outputs\quakeshield_map_data.csv"
OUTPUT_FILE = r"outputs\infrastructure_data.csv"

SEARCH_DISTANCE = 10000  # 10 km


# ============================================================
# OSM TAGS
# ============================================================

TAGS = {
    "amenity": ["hospital", "school"],
    "highway": True,
    "bridge": True
}


# ============================================================
# LOAD QUAKE SCENARIOS
# ============================================================

scenarios = pd.read_csv(INPUT_FILE)

print(
    f"QuakeShield scenarios: {len(scenarios)}"
)


all_records = []


# ============================================================
# COLLECT OSM INFRASTRUCTURE
# ============================================================

for _, scenario in scenarios.iterrows():

    earthquake_id = scenario["earthquake_id"]
    location_name = scenario["location_name"]

    latitude = scenario["latitude"]
    longitude = scenario["longitude"]

    print(
        f"\nCollecting infrastructure near: "
        f"{location_name}"
    )

    try:

        gdf = ox.features_from_point(
            (latitude, longitude),
            tags=TAGS,
            dist=SEARCH_DISTANCE
        )

        print(
            f"Infrastructure records: "
            f"{len(gdf)}"
        )

        for _, item in gdf.iterrows():

            # ------------------------------------------------
            # Determine infrastructure type
            # ------------------------------------------------

            infrastructure_type = None

            if pd.notna(item.get("amenity")):

                amenity = str(
                    item.get("amenity")
                ).lower()

                if amenity in [
                    "hospital",
                    "school"
                ]:
                    infrastructure_type = amenity

            if infrastructure_type is None:

                if pd.notna(item.get("bridge")):

                    infrastructure_type = "bridge"

            if infrastructure_type is None:

                if pd.notna(item.get("highway")):

                    highway = item.get(
                        "highway"
                    )

                    if isinstance(
                        highway,
                        list
                    ):
                        highway = highway[0]

                    infrastructure_type = str(
                        highway
                    )

            # ------------------------------------------------
            # Skip unknown records
            # ------------------------------------------------

            if infrastructure_type is None:
                continue

            # ------------------------------------------------
            # Get representative point
            #
            # OSM features can be:
            # Point / LineString / Polygon
            # ------------------------------------------------

            geometry = item.geometry

            if geometry is None:
                continue

            try:

                point = geometry.representative_point()

                infra_longitude = point.x
                infra_latitude = point.y

            except Exception:

                continue

            # ------------------------------------------------
            # Infrastructure name
            # ------------------------------------------------

            name = item.get(
                "name",
                ""
            )

            if pd.isna(name):
                name = ""

            # ------------------------------------------------
            # Save record
            # ------------------------------------------------

            all_records.append(
                {
                    "earthquake_id":
                        earthquake_id,

                    "location_name":
                        location_name,

                    "scenario_latitude":
                        latitude,

                    "scenario_longitude":
                        longitude,

                    "infrastructure_type":
                        infrastructure_type,

                    "name":
                        name,

                    "infra_latitude":
                        infra_latitude,

                    "infra_longitude":
                        infra_longitude
                }
            )

    except Exception as e:

        print(
            f"Could not collect data: {e}"
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

infrastructure_df = pd.DataFrame(
    all_records
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "outputs",
    exist_ok=True
)

infrastructure_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print(
    "INFRASTRUCTURE COLLECTION COMPLETED"
)
print("=" * 60)

print(
    f"Total infrastructure records: "
    f"{len(infrastructure_df)}"
)

if len(infrastructure_df) > 0:

    print("\nInfrastructure types:")

    print(
        infrastructure_df[
            "infrastructure_type"
        ]
        .value_counts()
        .to_string()
    )

print("\nSaved:")
print(OUTPUT_FILE)