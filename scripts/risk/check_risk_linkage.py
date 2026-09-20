import pandas as pd

# Load P1 and P2 prediction outputs
p1 = pd.read_csv("p1_prediction_outputs.csv")
p2 = pd.read_csv("p2_prediction_outputs.csv")

print("=" * 60)
print("RISK FUSION LINKAGE CHECK")
print("=" * 60)

print("\nP1 columns:")
print(list(p1.columns))

print("\nP2 columns:")
print(list(p2.columns))

print("\nP1 earthquake events:")
print(p1["earthquake_id"].nunique())

print("\nP2 countries:")
print(p2["Country"].nunique())

print("\nP2 regions:")
print(p2["Region"].nunique())

print("\nP2 sites:")
print(p2["Site"].nunique())

print("\nP1 sample:")
print(p1.head())

print("\nP2 sample:")
print(p2.head())

print("\nP1 geographic range:")
print("Latitude :", p1["latitude"].min(), "to", p1["latitude"].max())
print("Longitude:", p1["longitude"].min(), "to", p1["longitude"].max())

print("\nP2 seismic ranges:")
print("Mw  :", p2["Mw"].min(), "to", p2["Mw"].max())
print("PGA :", p2["PGA(g)"].min(), "to", p2["PGA(g)"].max())
