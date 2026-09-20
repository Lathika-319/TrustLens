import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier


# ============================================================
# LOAD DATASET
# ============================================================

file_path = r"data\raw\Database 7.xlsx"

df = pd.read_excel(file_path)

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# ============================================================
# TARGET
# ============================================================

target = "L"


# ============================================================
# FEATURES
# ============================================================

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


# ============================================================
# CONVERT FC (%) TO NUMERIC
# ============================================================

# Censored values such as <5, <12, >25 and >32
# are treated as missing.

df["FC (%)"] = pd.to_numeric(
    df["FC (%)"],
    errors="coerce"
)


# ============================================================
# CREATE MISSING-VALUE INDICATORS
# ============================================================

missing_columns = [
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)"
]

for col in missing_columns:
    df[col + "_missing"] = df[col].isna().astype(int)


# ============================================================
# FINAL FEATURE LIST
# ============================================================

p2_features = features + [
    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"
]


# ============================================================
# CREATE X AND y
# ============================================================

X = df[p2_features].copy()
y = df[target].copy()


# ============================================================
# FINAL P2 MODEL
# ============================================================

model = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "model",
        GradientBoostingClassifier(
            random_state=42
        )
    )
])


# ============================================================
# TRAIN ON COMPLETE DATASET
# ============================================================

print("\nTraining final P2 model...")

model.fit(X, y)


# ============================================================
# SAVE MODEL
# ============================================================

model_path = r"models\p2_liquefaction_model.joblib"

joblib.dump(model, model_path)


# ============================================================
# SAVE FEATURE LIST
# ============================================================

feature_path = "p2_features.txt"

with open(feature_path, "w", encoding="utf-8") as f:
    for feature in p2_features:
        f.write(feature + "\n")


# ============================================================
# TEST MODEL LOADING
# ============================================================

loaded_model = joblib.load(model_path)


# ============================================================
# CONFIRMATION
# ============================================================

print("\n" + "=" * 60)
print("FINAL P2 MODEL TRAINING COMPLETED")
print("=" * 60)

print("Model: Gradient Boosting")
print("Training samples:", len(X))
print("Features:", len(p2_features))

print("\nSaved files:")
print(model_path)
print(feature_path)

print("\nModel reload test: SUCCESS")
