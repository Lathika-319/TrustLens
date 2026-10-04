import pandas as pd
import joblib

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


DATA = r"TrustLens-push\data\QuakeShield_Final_Dataset_Slope.csv"

MODEL_OUT = r"TrustLens-push\models\p1_ground_failure_model_slope.joblib"


FEATURES = [
    "slope_degrees"
]

TARGET = "label"


print("=" * 70)
print("QUAKESHIELD P1 — FINAL EXPERIMENTAL SLOPE MODEL")
print("=" * 70)

df = pd.read_csv(DATA)

print(f"\nDataset rows: {len(df)}")
print(f"Features: {FEATURES}")

# Keep rows where the target exists
df = df.dropna(subset=[TARGET])

X = df[FEATURES]
y = df[TARGET]

print(f"Training rows: {len(df)}")
print(f"Positive labels: {(y == 1).sum()}")
print(f"Negative labels: {(y == 0).sum()}")

# Same pipeline used during LOEO evaluation
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("logreg", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

model.fit(X, y)

joblib.dump(model, MODEL_OUT)

print("\nMODEL TRAINED SUCCESSFULLY")
print(f"Saved to: {MODEL_OUT}")

print("\nFeatures used:")
for feature in FEATURES:
    print(f"  - {feature}")

print("\nIMPORTANT:")
print("This model outputs a relative Ground-Failure Model Score.")
print("It is NOT a calibrated probability.")

print("=" * 70)