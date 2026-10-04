import getpass
import json
import os
from pathlib import Path

import requests
import pandas as pd


BASE_URL = "https://nextgenerationliquefaction.org"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
}

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_token():
    print("=" * 70)
    print("NGL API AUTHENTICATION")
    print("=" * 70)

    email = input("NGL email/username: ").strip()
    password = getpass.getpass("NGL password: ")

    response = requests.get(
        f"{BASE_URL}/users/api-token",
        headers=HEADERS,
        auth=(email, password),
        timeout=30,
    )

    if response.status_code != 200:
        print("\nAuthentication failed.")
        print("Status:", response.status_code)
        print(response.text)
        raise SystemExit(1)

    payload = response.json()
    token = payload.get("token")

    if not token:
        print("No token returned.")
        print(payload)
        raise SystemExit(1)

    print("\nAuthentication: PASS")
    return token


def api_get_all(token, endpoint, limit=5000):
    """
    Download all pages from an NGL endpoint.
    """

    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"

    all_rows = []
    page = 1

    while True:

        print(
            f"Downloading {endpoint} | "
            f"page={page} | limit={limit}"
        )

        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            params={
                "limit": limit,
                "page": page,
                "includeUnreviewed": 0,
            },
            timeout=120,
        )

        if response.status_code != 200:
            print("\nAPI request failed.")
            print("Endpoint:", endpoint)
            print("Status:", response.status_code)
            print(response.text)
            raise SystemExit(1)

        rows = response.json()

        if not rows:
            break

        all_rows.extend(rows)

        print("  Rows:", len(rows))

        if len(rows) < limit:
            break

        page += 1

    print("Total rows:", len(all_rows))

    return pd.DataFrame(all_rows)


def save(df, filename):
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path}")
    return path


def main():

    token = get_token()

    print("\n" + "=" * 70)
    print("DOWNLOADING NGL DATA")
    print("=" * 70)

    # ------------------------------------------------------------
    # SITE
    # ------------------------------------------------------------

    sites = api_get_all(
        token,
        "/sites/api-index",
    )

    save(
        sites,
        "ngl_sites.csv",
    )

    # ------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------

    events = api_get_all(
        token,
        "/events/api-index",
    )

    save(
        events,
        "ngl_events.csv",
    )

    # ------------------------------------------------------------
    # FIELD OBSERVATIONS
    # ------------------------------------------------------------

    observations = api_get_all(
        token,
        "/field-observations/api-index",
    )

    save(
        observations,
        "ngl_field_observations.csv",
    )

    # ------------------------------------------------------------
    # LIQUEFACTION MANIFESTATIONS
    # ------------------------------------------------------------

    manifestations = api_get_all(
        token,
        "/liquefaction-manifestations/api-index",
    )

    save(
        manifestations,
        "ngl_liquefaction_manifestations.csv",
    )

    # ------------------------------------------------------------
    # DISPLACEMENT VECTORS
    # ------------------------------------------------------------

    displacement = api_get_all(
        token,
        "/displacement-vectors/api-index",
    )

    save(
        displacement,
        "ngl_displacement_vectors.csv",
    )

    # ------------------------------------------------------------
    # GROUND MOTION
    # ------------------------------------------------------------

    ground_motion = api_get_all(
        token,
        "/ground-motion-intensity-measurements/api-index",
    )

    save(
        ground_motion,
        "ngl_ground_motion.csv",
    )

    # ============================================================
    # AUDIT
    # ============================================================

    print("\n")
    print("=" * 70)
    print("NGL LATERAL SPREADING DATA AUDIT")
    print("=" * 70)

    print("\nDataset sizes")
    print("-" * 70)

    print("Sites:", len(sites))
    print("Events:", len(events))
    print("Field observations:", len(observations))
    print("Liquefaction manifestations:", len(manifestations))
    print("Displacement vectors:", len(displacement))
    print("Ground-motion records:", len(ground_motion))

    # ------------------------------------------------------------
    # Check lateral-spread labels
    # ------------------------------------------------------------

    print("\nLateral spread field")
    print("-" * 70)

    if "FLDM_LTSP" not in manifestations.columns:
        print("ERROR: FLDM_LTSP not found.")
        print(manifestations.columns.tolist())
        raise SystemExit(1)

    print(
        manifestations["FLDM_LTSP"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    # ------------------------------------------------------------
    # Coordinates
    # ------------------------------------------------------------

    valid_lat = manifestations["FLDM_LAT"].notna()
    valid_lon = manifestations["FLDM_LON"].notna()

    valid_coords = valid_lat & valid_lon

    invalid_zero_coords = (
        (manifestations["FLDM_LAT"] == 0)
        | (manifestations["FLDM_LON"] == 0)
    )

    print("\nCoordinates")
    print("-" * 70)

    print(
        "Manifestations with coordinates:",
        int(valid_coords.sum())
    )

    print(
        "Manifestations with zero coordinates:",
        int(invalid_zero_coords.sum())
    )

    # ------------------------------------------------------------
    # Positive lateral spreading cases
    # ------------------------------------------------------------

    lateral_yes = manifestations[
        manifestations["FLDM_LTSP"] == 1
    ].copy()

    lateral_no = manifestations[
        manifestations["FLDM_LTSP"] == 0
    ].copy()

    print("\nLateral-spreading cases")
    print("-" * 70)

    print(
        "YES:",
        len(lateral_yes)
    )

    print(
        "NO:",
        len(lateral_no)
    )

    # ------------------------------------------------------------
    # Positive cases with valid coordinates
    # ------------------------------------------------------------

    lateral_yes_valid = lateral_yes[
        lateral_yes["FLDM_LAT"].notna()
        & lateral_yes["FLDM_LON"].notna()
        & (lateral_yes["FLDM_LAT"] != 0)
        & (lateral_yes["FLDM_LON"] != 0)
    ].copy()

    print(
        "YES + valid coordinates:",
        len(lateral_yes_valid)
    )

    save(
        lateral_yes_valid,
        "ngl_lateral_spread_positive.csv",
    )

    # ------------------------------------------------------------
    # Negative cases with valid coordinates
    # ------------------------------------------------------------

    lateral_no_valid = lateral_no[
        lateral_no["FLDM_LAT"].notna()
        & lateral_no["FLDM_LON"].notna()
        & (lateral_no["FLDM_LAT"] != 0)
        & (lateral_no["FLDM_LON"] != 0)
    ].copy()

    print(
        "NO + valid coordinates:",
        len(lateral_no_valid)
    )

    save(
        lateral_no_valid,
        "ngl_lateral_spread_negative.csv",
    )

    # ------------------------------------------------------------
    # Observation IDs
    # ------------------------------------------------------------

    print("\nObservation linkage")
    print("-" * 70)

    if "FLDO_ID" in manifestations.columns:

        print(
            "Unique FLDO_ID:",
            manifestations["FLDO_ID"].nunique()
        )

        positive_ids = set(
            lateral_yes["FLDO_ID"].dropna()
        )

        negative_ids = set(
            lateral_no["FLDO_ID"].dropna()
        )

        print(
            "Positive observation IDs:",
            len(positive_ids)
        )

        print(
            "Negative observation IDs:",
            len(negative_ids)
        )

    # ------------------------------------------------------------
    # Displacement linkage
    # ------------------------------------------------------------

    if "FLDO_ID" in displacement.columns:

        positive_displacement = displacement[
            displacement["FLDO_ID"].isin(
                positive_ids
            )
        ].copy()

        print("\nDisplacement linked to positive cases")
        print("-" * 70)

        print(
            "Records:",
            len(positive_displacement)
        )

        print(
            "Unique observations:",
            positive_displacement["FLDO_ID"].nunique()
        )

        if len(positive_displacement) > 0:

            print(
                positive_displacement[
                    [
                        "FLDO_ID",
                        "FLDD_LAT",
                        "FLDD_LON",
                        "FLDD_AZIM",
                        "FLDD_HDIS",
                        "FLDD_VDIS",
                    ]
                ]
                .head(20)
                .to_string(index=False)
            )

    # ------------------------------------------------------------
    # Ground motion linkage
    # ------------------------------------------------------------

    if "FLDO_ID" in ground_motion.columns:

        positive_gm = ground_motion[
            ground_motion["FLDO_ID"].isin(
                positive_ids
            )
        ].copy()

        print("\nGround motion linked to positive cases")
        print("-" * 70)

        print(
            "Records:",
            len(positive_gm)
        )

        print(
            "Unique observations:",
            positive_gm["FLDO_ID"].nunique()
        )

        if len(positive_gm) > 0:

            print(
                positive_gm[
                    [
                        "FLDO_ID",
                        "GMIM_LAT",
                        "GMIM_LON",
                        "GMIM_TYPE",
                        "GMIM_VALUE",
                        "GMIM_UNIT",
                    ]
                ]
                .head(30)
                .to_string(index=False)
            )

    # ------------------------------------------------------------
    # Event linkage inspection
    # ------------------------------------------------------------

    print("\nField observation columns")
    print("-" * 70)

    print(observations.columns.tolist())

    print("\nManifestation columns")
    print("-" * 70)

    print(manifestations.columns.tolist())

    print("\nDisplacement columns")
    print("-" * 70)

    print(displacement.columns.tolist())

    print("\nGround-motion columns")
    print("-" * 70)

    print(ground_motion.columns.tolist())

    # ------------------------------------------------------------
    # Final message
    # ------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    print(
        "No P4 model was created."
    )

    print(
        "No existing QuakeShield model was modified."
    )

    print(
        "The output files contain only the audited NGL data."
    )


if __name__ == "__main__":
    main()