import pandas as pd

file_path = r"C:\Users\monik\Downloads\Liquefaction database (LIQ72833)\Liquefaction database (LIQ72833)\Database 7.xlsx"

df = pd.read_excel(file_path)

print("=== UNIQUE VALUES ===")

for col in df.columns:
    print(f"\n{col}")
    print("Unique:", df[col].nunique())
    print(df[col].dropna().unique()[:10])

print("\n=== NUMERIC SUMMARY ===")
print(df.describe().T)
