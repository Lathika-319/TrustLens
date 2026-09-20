import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
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

# The database contains censored values such as:
# <5, <12, >25, >32
#
# Their exact values are unknown, so they are treated as
# missing rather than assigning arbitrary numerical values.

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
# GROUP SPLIT BY REGION
# ============================================================

# We keep complete regions separate between training
# and testing to check geographic generalization.

groups = df["Region"]

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


print("\n" + "=" * 50)
print("GROUP SPLIT")
print("=" * 50)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining regions:")
print(sorted(groups.iloc[train_idx].unique()))

print("\nTesting regions:")
print(sorted(groups.iloc[test_idx].unique()))


# ============================================================
# MODELS
# ============================================================

models = {

    "Logistic Regression": Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ]),

    "Random Forest": Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "model",
            RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                n_jobs=-1
            )
        )
    ]),

    "Gradient Boosting": Pipeline([
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
}


# ============================================================
# TRAIN AND EVALUATE
# ============================================================

for name, model in models.items():

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    # Train
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Probability for positive class
    y_prob = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    # Print results
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)


print("\n" + "=" * 50)
print("P2 MODEL TRAINING COMPLETED")
print("=" * 50)
