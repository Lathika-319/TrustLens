import pandas as pd

file_path = r"C:\Users\monik\Downloads\Liquefaction database (LIQ72833)\Liquefaction database (LIQ72833)\Database 7.xlsx"

df = pd.read_excel(file_path)

features = [
    "σv/σv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)"
]

print("=== DUPLICATES ===")
print("Duplicate rows:", df.duplicated().sum())

print("\n=== TARGET BY MISSINGNESS ===")

for col in features:
    missing = df[col].isna()
    print(f"\n{col}")
    print("Missing rows:", missing.sum())
    print("L=1 among missing:", df.loc[missing, "L"].mean())
    print("L=1 among available:", df.loc[~missing, "L"].mean())

print("\n=== TARGET DISTRIBUTION ===")
print(df["L"].value_counts())
