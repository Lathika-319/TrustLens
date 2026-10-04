
# ============================================================
# QUAKESHIELD â€” P2 LIQUEFACTION HAZARD MODULE
# ============================================================
#
# Independent implementation of the production P2 model.
#
# Model:
#   GradientBoostingClassifier
#
# This module:
#   - loads the existing validated P2 model
#   - validates all 14 production features
#   - generates liquefaction model scores
#
# It does NOT:
#   - create risk levels
#   - combine P2 with P1
#   - create alerts
#   - claim calibrated probability
#   - perform spatial matching
# ============================================================

from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "p2_liquefaction_model.joblib"
)


# ============================================================
# REQUIRED FEATURES
# ============================================================

REQUIRED_FEATURES = [

    "Ïƒv/Ïƒv'",
    "(N1)60",
    "qt1N",
    "Ic",
    "VS1 (m/s)",
    "FC (%)",
    "Depth (m)",
    "Mw",
    "PGA(g)",

    "(N1)60_missing",
    "qt1N_missing",
    "Ic_missing",
    "VS1 (m/s)_missing",
    "FC (%)_missing"

]


# ============================================================
# MODULE METADATA
# ============================================================

MODULE_ID = "P2"

MODULE_NAME = "Liquefaction"

SCORE_FIELD = (
    "P2_liquefaction_model_score"
)

SCORE_TYPE = (
    "uncalibrated_model_indicator"
)


# ============================================================
# MODEL LOADING
# ============================================================

def load_model(model_file=None):

    if model_file is None:

        model_file = DEFAULT_MODEL_FILE

    model_file = Path(model_file)

    if not model_file.exists():

        raise FileNotFoundError(
            f"P2 model file not found: {model_file}"
        )

    return joblib.load(model_file)


# ============================================================
# FEATURE VALIDATION
# ============================================================

def validate_features(data):

    missing = [

        column

        for column in REQUIRED_FEATURES

        if column not in data.columns

    ]

    if missing:

        raise ValueError(
            "P2 input is missing required features: "
            + ", ".join(missing)
        )

    return True


# ============================================================
# SCORE GENERATION
# ============================================================

def predict_scores(
    data,
    model=None,
    model_file=None
):

    validate_features(data)

    if model is None:

        model = load_model(model_file)

    features = data[
        REQUIRED_FEATURES
    ].copy()

    scores = model.predict_proba(
        features
    )[:, 1]

    return pd.Series(
        scores,
        index=data.index,
        name=SCORE_FIELD
    )


# ============================================================
# ADD SCORES TO DATAFRAME
# ============================================================

def add_scores(
    data,
    model=None,
    model_file=None
):

    result = data.copy()

    result[SCORE_FIELD] = predict_scores(
        result,
        model=model,
        model_file=model_file
    )

    return result


# ============================================================
# MODULE INFORMATION
# ============================================================

def get_module_info():

    return {

        "id": MODULE_ID,

        "name": MODULE_NAME,

        "features":
            REQUIRED_FEATURES.copy(),

        "output_field":
            SCORE_FIELD,

        "score_type":
            SCORE_TYPE,

        "model_file":
            str(DEFAULT_MODEL_FILE)

    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("QUAKESHIELD â€” P2 LIQUEFACTION MODULE TEST")
    print("=" * 60)

    print()
    print(f"Module ID: {MODULE_ID}")
    print(f"Module name: {MODULE_NAME}")

    print()
    print("Required features:")

    for feature in REQUIRED_FEATURES:

        print(f"  - {feature}")

    print()
    print(
        f"Feature count: "
        f"{len(REQUIRED_FEATURES)}"
    )

    print()
    print(
        f"Model file: "
        f"{DEFAULT_MODEL_FILE}"
    )

    model = load_model()

    print()
    print("Model loading: PASS")

    # Small deterministic test dataset.
    #
    # Values are illustrative inputs only and are NOT
    # presented as scientific examples.

    test_data = pd.DataFrame({

        "Ïƒv/Ïƒv'": [0.8, 1.0, 1.2],

        "(N1)60": [10.0, 20.0, 30.0],

        "qt1N": [80.0, 120.0, 160.0],

        "Ic": [2.0, 2.2, 2.5],

        "VS1 (m/s)": [120.0, 180.0, 240.0],

        "FC (%)": [10.0, 20.0, 30.0],

        "Depth (m)": [5.0, 10.0, 15.0],

        "Mw": [6.9, 7.5, 7.6],

        "PGA(g)": [0.20, 0.40, 0.70],

        "(N1)60_missing": [0, 0, 0],

        "qt1N_missing": [0, 0, 0],

        "Ic_missing": [0, 0, 0],

        "VS1 (m/s)_missing": [0, 0, 0],

        "FC (%)_missing": [0, 0, 0]

    })

    scores = predict_scores(
        test_data,
        model=model
    )

    print()
    print("Prediction test: PASS")

    for index, score in scores.items():

        print(
            f"  Test row {index + 1}: "
            f"{score:.6f}"
        )

    print()
    print("P2 module test: PASS")

    print("=" * 60)
