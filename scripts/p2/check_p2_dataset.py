import pandas as pd

file_path = r"C:\Users\monik\Downloads\Liquefaction database (LIQ72833)\Liquefaction database (LIQ72833)\Database 7.xlsx"

df = pd.read_excel(file_path)

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nTarget distribution:")
print(df["L"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())
