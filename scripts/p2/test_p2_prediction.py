import pandas as pd
import joblib

# Load dataset
file_path = r"data\raw\Database 7.xlsx"
df = pd.read_excel(file_path)

# Load trained model
model = joblib.load(r"models\p2_liquefaction_model.joblib")

# Original P2 features
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

# Convert FC to numeric
df["FC (%)"] = pd.to_numeric(df["FC (%)"], errors="coerce")

# Create missing-value indicators
missing_columns = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for col in missing_columns:
    df[col + "_missing"] = df[col].isna().astype(int)

# Final 14 features
p2_features = features + [
    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"
]

# Select one real sample
sample = df[p2_features].iloc[[0]]

# Predict
prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0][1]

print("=" * 60)
print("P2 PREDICTION TEST")
print("=" * 60)

print("Predicted class:", prediction)
print("Liquefaction probability:", round(probability, 4))

if prediction == 1:
    print("Prediction: LIQUEFACTION")
else:
    print("Prediction: NO LIQUEFACTION")
