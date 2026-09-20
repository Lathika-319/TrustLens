import pandas as pd

# ============================================================
# P2 DATASET PREPARATION
# ============================================================

# Dataset path
file_path = r"data\raw\Database 7.xlsx"

# Load Excel file
df = pd.read_excel(file_path)

print("Dataset loaded successfully!")
print("Shape:", df.shape)

# ============================================================
# TARGET
# ============================================================

target = "L"

# ============================================================
# P2 FEATURES
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

# Values such as <5, <12, >25 and >32 do not give
# their exact numerical value.
# Therefore, treat these censored values as missing.
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
# DISPLAY INFORMATION
# ============================================================

print("\nP2 features:")
for feature in p2_features:
    print(feature)

print("\nFeature shape:", X.shape)
print("Target shape:", y.shape)

# ============================================================
# MISSING VALUES
# ============================================================

print("\nMissing-value counts:")

for col in p2_features:
    missing_count = X[col].isna().sum()

    if missing_count > 0:
        print(f"{col}: {missing_count}")

# ============================================================
# MISSING-VALUE INDICATORS
# ============================================================

print("\nMissing-value indicators:")

for col in missing_columns:
    indicator = col + "_missing"
    print(f"{indicator} = {X[indicator].sum()}")

# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\nTarget distribution:")

print(y.value_counts().sort_index())

print("\nTarget percentage:")

print(
    (y.value_counts(normalize=True).sort_index() * 100).round(2)
)

# ============================================================
# CHECK FOR NON-NUMERIC FEATURES
# ============================================================

print("\nNon-numeric feature check:")

for col in features:
    non_numeric = pd.to_numeric(
        df[col],
        errors="coerce"
    ).isna() & df[col].notna()

    print(
        f"{col}: {non_numeric.sum()} non-numeric values"
    )

print("\nP2 dataset preparation completed successfully!")
