import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

features = [
    "latitude",
    "longitude",
    "earthquake_magnitude",
    "earthquake_latitude",
    "earthquake_longitude",
    "earthquake_depth_km",
    "distance_to_epicenter_km",
    "elevation_m"
]

X = df[features]
y = df["label"]

# Handle missing values
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)

# Train Random Forest on all available P1 data
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_imputed, y)

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nP1 FEATURE IMPORTANCE")
print("=" * 60)

for feature, value in importance.items():
    print(f"{feature:30s} {value:.4f}")
