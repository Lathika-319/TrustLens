import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

file_path = r"data\raw\Database 7.xlsx"

df = pd.read_excel(file_path)

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

X = df[features].copy()
y = df["L"].copy()
groups = df["Region"]

# Add missing-value indicators
for col in features:
    if X[col].isna().any():
        X[col + "_missing"] = X[col].isna().astype(int)

# Keep 20% of regions completely unseen during testing
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(splitter.split(X, y, groups=groups))

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining regions:")
print(sorted(groups.iloc[train_idx].unique()))

print("\nTesting regions:")
print(sorted(groups.iloc[test_idx].unique()))

print("\nTraining target:")
print(y_train.value_counts())

print("\nTesting target:")
print(y_test.value_counts())
