import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut


DATA_PATH = "data/QuakeShield_Final_Dataset_Slope.csv"

FEATURES = [
    "distance_to_epicenter_km",
]

TARGET = "label"
GROUP = "earthquake_id"


df = pd.read_csv(DATA_PATH)

df = df.dropna(subset=[TARGET, GROUP])

X = df[FEATURES]
y = df[TARGET].astype(int)
groups = df[GROUP]

model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
])

logo = LeaveOneGroupOut()

results = []

for train_idx, test_idx in logo.split(X, y, groups):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    test_event = groups.iloc[test_idx].iloc[0]
    test_name = df.iloc[test_idx]["earthquake_name"].iloc[0]

    model.fit(X_train, y_train)

    scores = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, scores)

    results.append({
        "earthquake_id": test_event,
        "earthquake_name": test_name,
        "auc": auc,
    })

results_df = pd.DataFrame(results)

print("\nDISTANCE-ONLY P1 EXPERIMENT")
print("=" * 60)

print(results_df.to_string(index=False))

print("\nMean LOEO AUC:", round(results_df["auc"].mean(), 4))
print("Std LOEO AUC :", round(results_df["auc"].std(), 4))

print("\nCurrent slope-only mean LOEO AUC: 0.6466")

difference = results_df["auc"].mean() - 0.6466

print("Difference from slope-only:", round(difference, 4))