import pandas as pd

DATA_FILE = r"data\raw\Database 7.xlsx"

df = pd.read_excel(DATA_FILE, sheet_name="Liq database")

# Remove leading/trailing whitespace from country names
df["Country_clean"] = df["Country"].astype(str).str.strip()

checks = [
    ("Japan", "Tohoku"),
    ("Japan", "Niigata"),
    ("Japan", "Kobe"),
    ("Puerto Rico", "San Juan"),
    ("Indonesia", "Palu"),
    ("Indonesia", "Belanting"),
    ("Papua New Guinea", "Tari"),
    ("Colombia", "Mesetas"),
    ("Pakistan", "Kashmir"),
]

print("=" * 80)
print("QUAKESHIELD — P2 CORRECTED GEOGRAPHIC COVERAGE")
print("=" * 80)

for country, region_term in checks:

    country_rows = (
        df["Country_clean"] == country
    ).sum()

    region_matches = (
        df["Region"]
        .fillna("")
        .astype(str)
        .str.contains(
            region_term,
            case=False,
            regex=False
        )
        .sum()
    )

    print(
        f"{country:20} | "
        f"{region_term:12} | "
        f"country rows = {country_rows:4} | "
        f"region matches = {region_matches:4}"
    )

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)