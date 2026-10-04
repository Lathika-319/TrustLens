import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests


# ============================================================
# CONFIG
# ============================================================

INPUT_DATA = Path("data/QuakeShield_Final_Dataset_Slope.csv")
OUTPUT_DATA = Path("data/QuakeShield_Final_Dataset_Slope_PGA.csv")

CACHE_DIR = Path("data/raw/shakemap_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

USGS_EVENT_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{}.geojson"
)

PGA_FILE = "coverage_pga_high_res.covjson"

EARTH_RADIUS_KM = 6371.0088


# ============================================================
# HELPERS
# ============================================================

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two latitude/longitude points."""

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    )

    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def get_atlas_pga_url(event_id):
    """
    Query the official USGS event endpoint and select
    the newest Atlas ShakeMap containing high-resolution PGA.
    """

    url = USGS_EVENT_URL.format(event_id)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    event = response.json()

    products = event.get("properties", {}).get("products", {})
    shakemaps = products.get("shakemap", [])

    candidates = []

    for product in shakemaps:
        if product.get("source") != "atlas":
            continue

        contents = product.get("contents", {})

        if f"download/{PGA_FILE}" not in contents:
            continue

        update_time = product.get("updateTime", 0)

        product_id = product.get("id", "")

        # Product ID format:
        # urn:usgs-product:atlas:shakemap:<event>:<timestamp>
        parts = product_id.split(":")

        if len(parts) < 6:
            continue

        timestamp = parts[-1]

        pga_url = (
            f"https://earthquake.usgs.gov/product/shakemap/"
            f"{event_id}/atlas/{timestamp}/{f'download/{PGA_FILE}'}"
        )

        candidates.append(
            {
                "update_time": update_time,
                "product_id": product_id,
                "url": pga_url,
            }
        )

    if not candidates:
        raise RuntimeError(
            f"No Atlas ShakeMap with {PGA_FILE} found for {event_id}"
        )

    # Newest Atlas product
    selected = max(candidates, key=lambda x: x["update_time"])

    return selected


def download_covjson(event_id, url):
    """Download and cache CoverageJSON."""

    cache_file = CACHE_DIR / f"{event_id}_pga.covjson"

    if cache_file.exists() and cache_file.stat().st_size > 0:
        print(f"  Using cached file: {cache_file}")
        return cache_file

    print(f"  Downloading PGA grid...")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    cache_file.write_bytes(response.content)

    print(
        f"  Saved: {cache_file} "
        f"({len(response.content) / 1024:.1f} KB)"
    )

    return cache_file


def parse_covjson(path):
    """
    Parse USGS PGA CoverageJSON.

    USGS CoverageJSON stores PGA as ln(g).
    Convert to actual PGA in g using exp().
    """

    with open(path, "r", encoding="utf-8") as f:
        cov = json.load(f)

    domain = cov["domain"]
    axes = domain["axes"]

    x_axis = axes["x"]
    y_axis = axes["y"]

    x = np.linspace(
        x_axis["start"],
        x_axis["stop"],
        x_axis["num"],
    )

    y = np.linspace(
        y_axis["start"],
        y_axis["stop"],
        y_axis["num"],
    )

    pga_values = np.asarray(
        cov["ranges"]["PGA"]["values"],
        dtype=float,
    )

    shape = cov["ranges"]["PGA"]["shape"]

    pga_values = pga_values.reshape(shape)

    # CoverageJSON PGA is ln(g)
    pga_g = np.exp(pga_values)

    return x, y, pga_g


def match_cells(df, x, y, pga_g):
    """
    Match each QuakeShield assessment cell to the nearest
    ShakeMap grid cell.
    """

    lon_values = df["longitude"].to_numpy(dtype=float)
    lat_values = df["latitude"].to_numpy(dtype=float)

    matched_pga = np.full(len(df), np.nan)
    grid_distance = np.full(len(df), np.nan)

    for i, (lat, lon) in enumerate(zip(lat_values, lon_values)):

        xi = np.abs(x - lon).argmin()
        yi = np.abs(y - lat).argmin()

        matched_lon = x[xi]
        matched_lat = y[yi]

        matched_pga[i] = pga_g[yi, xi]

        grid_distance[i] = haversine_km(
            lat,
            lon,
            matched_lat,
            matched_lon,
        )

    return matched_pga, grid_distance


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("QUAKESHIELD — USGS SHAKEMAP PGA DATASET BUILDER")
    print("=" * 70)

    if not INPUT_DATA.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_DATA}"
        )

    df = pd.read_csv(INPUT_DATA)

    required_columns = [
        "earthquake_id",
        "earthquake_name",
        "latitude",
        "longitude",
        "label",
        "slope_degrees",
        "distance_to_epicenter_km",
    ]

    missing = [
        c for c in required_columns
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(f"\nInput rows: {len(df):,}")

    events = (
        df[
            [
                "earthquake_id",
                "earthquake_name",
            ]
        ]
        .drop_duplicates("earthquake_id")
        .reset_index(drop=True)
    )

    print(f"Earthquake events: {len(events)}")

    result_parts = []

    # ========================================================
    # PROCESS EACH EVENT
    # ========================================================

    for event_number, row in enumerate(
        events.itertuples(index=False),
        start=1,
    ):

        event_id = row.earthquake_id
        event_name = row.earthquake_name

        print("\n" + "-" * 70)
        print(
            f"[{event_number}/{len(events)}] "
            f"{event_name}"
        )
        print(f"Event ID: {event_id}")

        # ----------------------------------------------------
        # Discover official USGS Atlas ShakeMap
        # ----------------------------------------------------

        product = get_atlas_pga_url(event_id)

        print(f"  ShakeMap product:")
        print(f"  {product['product_id']}")
        print(f"  PGA URL:")
        print(f"  {product['url']}")

        # ----------------------------------------------------
        # Download / cache
        # ----------------------------------------------------

        covjson_path = download_covjson(
            event_id,
            product["url"],
        )

        # ----------------------------------------------------
        # Parse
        # ----------------------------------------------------

        x, y, pga_g = parse_covjson(
            covjson_path
        )

        print(
            f"  ShakeMap grid: "
            f"{len(x)} x {len(y)}"
        )

        print(
            f"  PGA range: "
            f"{np.nanmin(pga_g):.4f} – "
            f"{np.nanmax(pga_g):.4f} g"
        )

        # ----------------------------------------------------
        # Select event cells
        # ----------------------------------------------------

        event_mask = (
            df["earthquake_id"] == event_id
        )

        event_df = df.loc[event_mask].copy()

        print(
            f"  QuakeShield cells: "
            f"{len(event_df):,}"
        )

        # ----------------------------------------------------
        # Match PGA
        # ----------------------------------------------------

        matched_pga, grid_distance = match_cells(
            event_df,
            x,
            y,
            pga_g,
        )

        event_df["PGA_g"] = matched_pga

        event_df["shakemap_grid_distance_km"] = (
            grid_distance
        )

        event_df["shakemap_source"] = "USGS ShakeMap Atlas"

        event_df["shakemap_product_id"] = (
            product["product_id"]
        )

        event_df["shakemap_pga_unit"] = "g"

        result_parts.append(event_df)

        print(
            f"  Matched PGA rows: "
            f"{event_df['PGA_g'].notna().sum():,}"
        )

        print(
            f"  PGA range on cells: "
            f"{event_df['PGA_g'].min():.4f} – "
            f"{event_df['PGA_g'].max():.4f} g"
        )

        print(
            f"  Grid-match distance: "
            f"{event_df['shakemap_grid_distance_km'].min():.4f} – "
            f"{event_df['shakemap_grid_distance_km'].max():.4f} km"
        )

    # ========================================================
    # COMBINE
    # ========================================================

    result = pd.concat(
        result_parts,
        ignore_index=True,
    )

    # Preserve original row order as closely as possible
    # using the original identifying columns.
    result = result.reset_index(drop=True)

    # ========================================================
    # FINAL AUDIT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL DATASET AUDIT")
    print("=" * 70)

    print(f"Rows: {len(result):,}")

    print(
        f"PGA non-null: "
        f"{result['PGA_g'].notna().sum():,}"
    )

    print(
        f"PGA missing: "
        f"{result['PGA_g'].isna().sum():,}"
    )

    print(
        f"PGA min: "
        f"{result['PGA_g'].min():.6f} g"
    )

    print(
        f"PGA max: "
        f"{result['PGA_g'].max():.6f} g"
    )

    print(
        f"PGA mean: "
        f"{result['PGA_g'].mean():.6f} g"
    )

    print(
        f"Grid-match distance max: "
        f"{result['shakemap_grid_distance_km'].max():.6f} km"
    )

    print("\nRows by earthquake:")

    summary = (
        result
        .groupby(
            [
                "earthquake_id",
                "earthquake_name",
            ],
            as_index=False,
        )
        .agg(
            rows=("PGA_g", "size"),
            pga_min=("PGA_g", "min"),
            pga_mean=("PGA_g", "mean"),
            pga_max=("PGA_g", "max"),
            match_distance_max=(
                "shakemap_grid_distance_km",
                "max",
            ),
        )
    )

    print(
        summary.to_string(index=False)
    )

    # ========================================================
    # SAVE
    # ========================================================

    result.to_csv(
        OUTPUT_DATA,
        index=False,
    )

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        f"Saved experimental dataset:\n"
        f"{OUTPUT_DATA}"
    )

    print(
        "\nIMPORTANT:"
        "\nThis dataset is for earthquake-aware experiments."
        "\nThe existing slope-only P1 dataset/model has NOT been modified."
    )


if __name__ == "__main__":
    main()