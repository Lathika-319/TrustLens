import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
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
    roc_auc_score
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
# are treated as missing because their exact values
# are not known.

df["FC (%)"] = pd.to_numeric(
    df["FC (%)"],
    errors="coerce"
)


# ============================================================
# MISSING-VALUE INDICATORS
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
# X, y AND GROUPS
# ============================================================

X = df[p2_features].copy()

y = df[target].copy()

groups = df["Region"]


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
# 5-FOLD GROUP CROSS-VALIDATION
# ============================================================

group_kfold = GroupKFold(n_splits=5)


for name, model in models.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    accuracies = []
    precisions = []
    recalls = []
    f1_scores = []
    roc_aucs = []

    for fold, (train_idx, test_idx) in enumerate(
        group_kfold.split(X, y, groups),
        start=1
    ):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        # Train
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Probabilities
        y_prob = model.predict_proba(X_test)[:, 1]

        # Metrics
        accuracy = accuracy_score(
            y_test,
            y_pred
        )

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

        # Store
        accuracies.append(accuracy)
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        roc_aucs.append(roc_auc)

        # Print fold result
        print(
            f"Fold {fold}: "
            f"Accuracy={accuracy:.4f}, "
            f"Precision={precision:.4f}, "
            f"Recall={recall:.4f}, "
            f"F1={f1:.4f}, "
            f"ROC-AUC={roc_auc:.4f}"
        )

    # ========================================================
    # OVERALL RESULTS
    # ========================================================

    print("\nOverall:")
    print(
        f"Accuracy : "
        f"{np.mean(accuracies):.4f} +/- {np.std(accuracies):.4f}"
    )

    print(
        f"Precision: "
        f"{np.mean(precisions):.4f} +/- {np.std(precisions):.4f}"
    )

    print(
        f"Recall   : "
        f"{np.mean(recalls):.4f} +/- {np.std(recalls):.4f}"
    )

    print(
        f"F1 Score : "
        f"{np.mean(f1_scores):.4f} +/- {np.std(f1_scores):.4f}"
    )

    print(
        f"ROC-AUC  : "
        f"{np.mean(roc_aucs):.4f} +/- {np.std(roc_aucs):.4f}"
    )


print("\n" + "=" * 60)
print("P2 CROSS-VALIDATION COMPLETED")
print("=" * 60)
