import pandas as pd
import joblib

DATA_FILE = r"data\raw\Database 7.xlsx"
MODEL_FILE = r"models\p2_liquefaction_model.joblib"

TARGET_MWS = [5.6, 6.4, 6.6, 6.9, 7.5, 7.6, 9.1]

print("=" * 70)
print("QUAKESHIELD — P2 STABILITY AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
df = pd.read_excel(DATA_FILE, sheet_name="Liq database")

# Load trained model
model = joblib.load(MODEL_FILE)

print(f"\nP2 rows: {len(df)}")

# ------------------------------------------------------------
# Reproduce EXACT preprocessing used during training
# ------------------------------------------------------------

# Convert FC (%) to numeric.
# Values such as "<5" become NaN, matching training behavior.
df["FC (%)"] = pd.to_numeric(
    df["FC (%)"],
    errors="coerce"
)

# Create the same missing-indicator columns used during training
missing_base_features = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for col in missing_base_features:
    missing_col = f"{col}_missing"
    df[missing_col] = df[col].isna().astype(int)

# ------------------------------------------------------------
# Use EXACT feature order stored in trained model
# ------------------------------------------------------------

features = list(model.feature_names_in_)

print("\nModel features:")
for feature in features:
    print(f"  - {feature}")

# ------------------------------------------------------------
# Predict P2 scores
# ------------------------------------------------------------

X = df[features]

df["p2_score"] = model.predict_proba(X)[:, 1]

print("\nP2 score range:")
print(f"  Min: {df['p2_score'].min():.4f}")
print(f"  Max: {df['p2_score'].max():.4f}")

# ------------------------------------------------------------
# Stability by magnitude
# ------------------------------------------------------------

summary = (
    df[df["Mw"].isin(TARGET_MWS)]
    .groupby("Mw")["p2_score"]
    .agg(
        sites="count",
        mean="mean",
        median="median",
        std="std",
        minimum="min",
        maximum="max",
    )
    .reindex(TARGET_MWS)
)

print("\n" + "=" * 70)
print("P2 SCORE STABILITY BY MATCHED MAGNITUDE")
print("=" * 70)

print(summary.to_string(float_format=lambda x: f"{x:.4f}"))

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)