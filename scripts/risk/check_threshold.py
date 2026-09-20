import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score

# Load dataset
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
groups = df["earthquake_id"]

# Same group-aware split used earlier
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

# Gradient Boosting
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", GradientBoostingClassifier(random_state=42))
])

model.fit(X_train, y_train)

# Probability of landslide (class 1)
y_prob = model.predict_proba(X_test)[:, 1]

print("\nP1 THRESHOLD ANALYSIS")
print("=" * 70)

for threshold in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:

    y_pred = (y_prob >= threshold).astype(int)

    precision = precision_score(
        y_test, y_pred, zero_division=0
    )

    recall = recall_score(
        y_test, y_pred, zero_division=0
    )

    f1 = f1_score(
        y_test, y_pred, zero_division=0
    )

    print(
        f"Threshold: {threshold:.2f} | "
        f"Precision: {precision:.4f} | "
        f"Recall: {recall:.4f} | "
        f"F1: {f1:.4f}"
    )
