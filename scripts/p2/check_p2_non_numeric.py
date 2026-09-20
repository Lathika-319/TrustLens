import pandas as pd

file_path = r"data\raw\Database 7.xlsx"

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

for col in features:
    non_numeric = pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()

    if non_numeric.any():
        print("\n" + "=" * 50)
        print(col)
        print("Non-numeric count:", non_numeric.sum())
        print("Values:")
        print(df.loc[non_numeric, col].value_counts().head(20))
