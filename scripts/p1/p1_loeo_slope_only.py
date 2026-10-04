import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score


DATA = r"data\QuakeShield_Final_Dataset_Slope.csv"

FEATURES = [
    "slope_degrees"
]

TARGET = "label"
GROUP = "earthquake_name"


df = pd.read_csv(DATA)

df = df.dropna(subset=[TARGET, GROUP])

results = []

events = df[GROUP].unique()

for event in events:

    train = df[df[GROUP] != event].copy()
    test = df[df[GROUP] == event].copy()

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(
            max_iter=1000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)

    auc = roc_auc_score(y_test, prob)
    f1 = f1_score(y_test, pred, zero_division=0)
    precision = precision_score(y_test, pred, zero_division=0)
    recall = recall_score(y_test, pred, zero_division=0)

    results.append({
        "earthquake_name": event,
        "n": len(test),
        "positive": int(y_test.sum()),
        "negative": int((y_test == 0).sum()),
        "AUC": auc,
        "F1": f1,
        "Precision": precision,
        "Recall": recall
    })

results_df = pd.DataFrame(results)

print("\nSLOPE-ONLY LOEO RESULTS")
print("=" * 70)

print(
    results_df[
        [
            "earthquake_name",
            "n",
            "positive",
            "negative",
            "AUC",
            "F1",
            "Precision",
            "Recall"
        ]
    ].to_string(index=False)
)

print("\nSUMMARY")
print("=" * 70)

print(f"Mean AUC       : {results_df['AUC'].mean():.4f}")
print(f"Median AUC     : {results_df['AUC'].median():.4f}")
print(f"Mean F1        : {results_df['F1'].mean():.4f}")
print(f"Mean Precision : {results_df['Precision'].mean():.4f}")
print(f"Mean Recall    : {results_df['Recall'].mean():.4f}")

out = r"outputs\p1_loeo_slope_only_results.csv"
results_df.to_csv(out, index=False)

print(f"\nSaved: {out}")
