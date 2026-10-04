import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


DATA = r"TrustLens-push\data\QuakeShield_Final_Dataset_Slope.csv"

FEATURES = [
    "slope_degrees"
]

TARGET = "label"
GROUP = "earthquake_name"

N_PERMUTATIONS = 100
SEED = 42


df = pd.read_csv(DATA)
df = df.dropna(subset=[TARGET, GROUP])

events = df[GROUP].unique()


def run_loeo(data):

    aucs = []

    for event in events:

        train = data[data[GROUP] != event].copy()
        test = data[data[GROUP] == event].copy()

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

        aucs.append(
            roc_auc_score(y_test, prob)
        )

    return np.mean(aucs)


print("\nSLOPE-ONLY LOEO LABEL-PERMUTATION TEST")
print("=" * 70)
print(f"Features     : {FEATURES}")
print(f"Events       : {len(events)}")
print(f"Permutations : {N_PERMUTATIONS}")
print(f"Seed         : {SEED}")


observed = run_loeo(df)

print(f"\nObserved LOEO mean AUC: {observed:.4f}")


rng = np.random.default_rng(SEED)

permutation_scores = []

for i in range(N_PERMUTATIONS):

    permuted = df.copy()

    # Shuffle labels independently within each earthquake
    for event in events:

        mask = permuted[GROUP] == event

        labels = permuted.loc[mask, TARGET].to_numpy()

        permuted.loc[mask, TARGET] = rng.permutation(labels)

    score = run_loeo(permuted)

    permutation_scores.append(score)


permutation_scores = np.array(permutation_scores)


print("\nPermutation distribution")
print("-" * 70)

print(f"Mean : {permutation_scores.mean():.4f}")
print(f"Std  : {permutation_scores.std():.4f}")
print(f"Min  : {permutation_scores.min():.4f}")
print(f"Max  : {permutation_scores.max():.4f}")

print(f"P5   : {np.percentile(permutation_scores, 5):.4f}")
print(f"P50  : {np.percentile(permutation_scores, 50):.4f}")
print(f"P95  : {np.percentile(permutation_scores, 95):.4f}")


ge = np.sum(permutation_scores >= observed)

p_value = (ge + 1) / (N_PERMUTATIONS + 1)

print(f"\nPermutations >= observed: {ge} / {N_PERMUTATIONS}")
print(f"Empirical one-sided p-value: {p_value:.4f}")