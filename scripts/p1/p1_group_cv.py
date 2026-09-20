import pandas as pd

from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score

# Load dataset
df = pd.read_csv("data/QuakeShield_Final_Dataset.csv")

# P1 features without geographic coordinates
features = [
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

# Models
models = {
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

# 5-fold group cross-validation
cv = GroupKFold(n_splits=5)

scoring = {
    "accuracy": "accuracy",
    "precision": make_scorer(
        precision_score,
        zero_division=0
    ),
    "recall": make_scorer(
        recall_score,
        zero_division=0
    ),
    "f1": make_scorer(
        f1_score,
        zero_division=0
    ),
    "roc_auc": "roc_auc"
}

print("\nP1 GROUP CROSS-VALIDATION")
print("=" * 80)
print("Testing generalization across unseen earthquake events")
print("=" * 80)

for name, model in models.items():

    results = cross_validate(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    print(f"\n{name}")
    print("-" * 80)

    for metric in scoring:
        scores = results[f"test_{metric}"]

        print(
            f"{metric.upper():10s}: "
            f"{scores.mean():.4f} "
            f"+/- {scores.std():.4f}"
        )
