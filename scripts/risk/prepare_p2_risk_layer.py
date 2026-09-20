import pandas as pd
import joblib

# =========================
# LOAD P2 DATA
# =========================

file_path = r"data\raw\Database 7.xlsx"
df = pd.read_excel(file_path)

print("P2 dataset loaded successfully!")
print("Rows:", len(df))

# =========================
# LOAD FINAL P2 MODEL
# =========================

model = joblib.load(r"models\p2_liquefaction_model.joblib")

# =========================
# PREPARE FEATURES
# =========================

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

# Convert censored FC values to missing
df["FC (%)"] = pd.to_numeric(
    df["FC (%)"],
    errors="coerce"
)

missing_columns = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for col in missing_columns:
    df[col + "_missing"] = df[col].isna().astype(int)

p2_features = features + [
    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"
]

X = df[p2_features]

# =========================
# GENERATE PROBABILITIES
# =========================

df["P2_liquefaction_probability"] = (
    model.predict_proba(X)[:, 1]
)

# =========================
# CREATE RISK LAYER
# =========================

risk_layer = df[
    [
        "Country",
        "Region",
        "Site",
        "Mw",
        "PGA(g)",
        "Depth (m)",
        "P2_liquefaction_probability"
    ]
].copy()

# =========================
# SAVE
# =========================

output_file = "p2_risk_layer.csv"

risk_layer.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 60)
print("P2 RISK LAYER CREATED")
print("=" * 60)

print("Rows:", len(risk_layer))
print("Columns:", len(risk_layer.columns))

print("\nProbability range:")
print(
    round(
        risk_layer["P2_liquefaction_probability"].min(),
        4
    ),
    "to",
    round(
        risk_layer["P2_liquefaction_probability"].max(),
        4
    )
)

print("\nSaved file:")
print(output_file)

print("\nSample:")
print(risk_layer.head())
