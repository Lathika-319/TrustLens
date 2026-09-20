import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# ============================================================
# 2. DEFINE P1 FEATURES AND TARGET
# ============================================================

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

# earthquake_id is used ONLY for grouping.
groups = df["earthquake_id"]


# ============================================================
# 3. GROUP-AWARE TRAIN/TEST SPLIT
# ============================================================

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

groups_train = groups.iloc[train_idx]
groups_test = groups.iloc[test_idx]


print("\nTrain/Test Split")
print("=" * 60)

print("Training rows:", len(X_train))
print("Testing rows :", len(X_test))

print("\nTraining earthquakes:")
print(groups_train.unique())

print("\nTesting earthquakes:")
print(groups_test.unique())


# ============================================================
# 4. DEFINE MODELS
# ============================================================

models = {

    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=1000,
            random_state=42
        ))
    ]),

    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        ))
    ]),

    "Gradient Boosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", GradientBoostingClassifier(
            random_state=42
        ))
    ])
}


# ============================================================
# 5. TRAIN AND EVALUATE
# ============================================================

print("\n\nMODEL RESULTS")
print("=" * 80)

for name, model in models.items():

    print(f"\n{name}")
    print("-" * 80)

    # Train
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)

    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)
