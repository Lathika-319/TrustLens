import os
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)

DATA_FILE = r"outputs\p4_lateral_spreading_clean_dataset.csv"
OUTPUT_FILE = r"outputs\p4_loeo_results.csv"
MODEL_FILE = r"models\p4_lateral_spreading_model.joblib"


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(DATA_FILE)

FEATURES = [
    "PGA_g",
    "PGV_mps",
    "Arias_Intensity",
]

TARGET = "lateral_spreading"
GROUP = "EVNT_ID"

print("=" * 70)
print("QUAKESHIELD — P4 LATERAL SPREADING LOEO VALIDATION")
print("=" * 70)

print(f"\nDataset rows: {len(df)}")
print(f"Events: {df[GROUP].nunique()}")

print("\nFeatures:")
for f in FEATURES:
    print(f"  {f}")

print(f"\nTarget: {TARGET}")


# ============================================================
# BASIC VALIDATION
# ============================================================

required = FEATURES + [TARGET, GROUP]

missing_columns = [
    c for c in required
    if c not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nTarget distribution:")
print(
    df[TARGET]
    .value_counts()
    .sort_index()
)


# ============================================================
# MODEL
# ============================================================

model = Pipeline(
    steps=[
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
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ]
)


# ============================================================
# LEAVE-ONE-EARTHQUAKE-OUT
# ============================================================

events = sorted(
    df[GROUP].dropna().unique()
)

results = []

all_true = []
all_score = []

print("\n" + "=" * 70)
print("LOEO RESULTS")
print("=" * 70)

for event_id in events:

    train = df[df[GROUP] != event_id].copy()
    test = df[df[GROUP] == event_id].copy()

    y_train = train[TARGET].astype(int)
    y_test = test[TARGET].astype(int)

    # Cannot train if training fold contains one class.
    if y_train.nunique() < 2:
        print(
            f"Event {event_id}: SKIPPED — "
            f"training fold has one class"
        )
        continue

    model.fit(
        train[FEATURES],
        y_train,
    )

    scores = model.predict_proba(
        test[FEATURES]
    )[:, 1]

    all_true.extend(
        y_test.tolist()
    )

    all_score.extend(
        scores.tolist()
    )

    # Event-level AUC only when test contains both classes.
    if y_test.nunique() == 2:
        event_auc = roc_auc_score(
            y_test,
            scores,
        )
    else:
        event_auc = np.nan

    results.append(
        {
            "EVNT_ID": event_id,
            "EVNT_NM": test["EVNT_NM"].iloc[0],
            "n_test": len(test),
            "positive_test": int(y_test.sum()),
            "negative_test": int((y_test == 0).sum()),
            "event_auc": event_auc,
            "mean_score": float(scores.mean()),
            "max_score": float(scores.max()),
        }
    )

    auc_text = (
        f"{event_auc:.4f}"
        if not np.isnan(event_auc)
        else "N/A"
    )

    print(
        f"Event {event_id:>3} | "
        f"{test['EVNT_NM'].iloc[0][:35]:35s} | "
        f"n={len(test):2d} | "
        f"pos={int(y_test.sum()):2d} | "
        f"AUC={auc_text}"
    )


# ============================================================
# OVERALL OUT-OF-FOLD METRICS
# ============================================================

all_true = np.array(all_true)
all_score = np.array(all_score)

print("\n" + "=" * 70)
print("OVERALL OUT-OF-FOLD METRICS")
print("=" * 70)

overall_auc = roc_auc_score(
    all_true,
    all_score,
)

pr_auc = average_precision_score(
    all_true,
    all_score,
)

print(
    f"LOEO ROC-AUC : {overall_auc:.4f}"
)

print(
    f"LOEO PR-AUC  : {pr_auc:.4f}"
)


# ============================================================
# THRESHOLD METRICS
# ============================================================

threshold = 0.5

pred = (
    all_score >= threshold
).astype(int)

precision = precision_score(
    all_true,
    pred,
    zero_division=0,
)

recall = recall_score(
    all_true,
    pred,
    zero_division=0,
)

f1 = f1_score(
    all_true,
    pred,
    zero_division=0,
)

print("\nThreshold = 0.5")

print(
    f"Precision    : {precision:.4f}"
)

print(
    f"Recall       : {recall:.4f}"
)

print(
    f"F1           : {f1:.4f}"
)


# ============================================================
# EVENT-LEVEL SUMMARY
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\nSaved:")
print(OUTPUT_FILE)


# ============================================================
# TRAIN FINAL CANDIDATE ON ALL DATA
# ============================================================

print("\n" + "=" * 70)
print("TRAINING FINAL P4 CANDIDATE")
print("=" * 70)

model.fit(
    df[FEATURES],
    df[TARGET],
)

os.makedirs(
    os.path.dirname(MODEL_FILE),
    exist_ok=True,
)

import joblib

joblib.dump(
    model,
    MODEL_FILE,
)

print(
    f"Saved model: {MODEL_FILE}"
)


# ============================================================
# COEFFICIENTS
# ============================================================

classifier = model.named_steps[
    "classifier"
]

print("\n" + "=" * 70)
print("MODEL COEFFICIENTS")
print("=" * 70)

for feature, coefficient in zip(
    FEATURES,
    classifier.coef_[0],
):

    print(
        f"{feature:20s}: "
        f"{coefficient:+.6f}"
    )


# ============================================================
# FINAL VERDICT
# ============================================================

print("\n" + "=" * 70)
print("P4 LOEO COMPLETE")
print("=" * 70)

print(
    f"LOEO ROC-AUC = {overall_auc:.4f}"
)

print(
    f"LOEO PR-AUC  = {pr_auc:.4f}"
)

print(
    "\nIMPORTANT:"
)

print(
    "This is a candidate model only."
)

print(
    "LOEO performance is not proof of future generalization."
)

print(
    "The model has NOT been connected to the production pipeline."
)