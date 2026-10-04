import os
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "data/QuakeShield_Final_Dataset_Slope_PGA.csv"

MODEL_PATH = "models/p1_ground_failure_model_slope_pga.joblib"

FEATURES = [
    "slope_degrees",
    "PGA_g",
]

TARGET = "label"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 75)
print("QUAKESHIELD — TRAIN P1 SLOPE + PGA MODEL")
print("=" * 75)

print(f"\nLoading dataset:")
print(DATA_PATH)

df = pd.read_csv(DATA_PATH)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# ============================================================
# VALIDATION
# ============================================================

required_columns = FEATURES + [TARGET]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

print("\nRequired columns found:")
for column in required_columns:
    print(f"  ✓ {column}")

print("\nTarget distribution:")

print(
    df[TARGET]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nMissing values:")

for column in FEATURES:
    missing_count = df[column].isna().sum()

    print(
        f"  {column}: "
        f"{missing_count:,} "
        f"({missing_count / len(df) * 100:.2f}%)"
    )


# ============================================================
# FEATURES / TARGET
# ============================================================

X = df[FEATURES]
y = df[TARGET]


# ============================================================
# MODEL
# ============================================================

model = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42,
            ),
        ),
    ]
)


# ============================================================
# TRAIN
# ============================================================

print("\n" + "=" * 75)
print("TRAINING")
print("=" * 75)

print(
    "\nFeatures used:"
)

for feature in FEATURES:
    print(f"  • {feature}")

print(
    "\nTraining on all prepared historical "
    "assessment samples..."
)

model.fit(X, y)

print("✓ Training complete")


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_PATH),
    exist_ok=True,
)

joblib.dump(
    model,
    MODEL_PATH,
)

print("\n" + "=" * 75)
print("MODEL SAVED")
print("=" * 75)

print(
    f"\nSaved to:\n{MODEL_PATH}"
)


# ============================================================
# MODEL INFORMATION
# ============================================================

classifier = model.named_steps["classifier"]

print("\nModel:")
print(
    "Median Imputation → StandardScaler → "
    "LogisticRegression"
)

print(
    f"\nNumber of features: "
    f"{len(FEATURES)}"
)

print(
    "\nFeatures:"
)

for feature in FEATURES:
    print(f"  • {feature}")

print(
    "\nIMPORTANT:"
)

print(
    "This is an experimental P1 candidate model."
)

print(
    "The existing slope-only production model "
    "has not been replaced."
)

print(
    "\nDone."
)