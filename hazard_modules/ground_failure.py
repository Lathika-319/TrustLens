
# ============================================================
# QUAKESHIELD â€” P1 GROUND FAILURE HAZARD MODULE
# ============================================================
#
# Independent implementation of the production P1 model.
#
# Model:
#   Slope + PGA
#
# This module:
#   - loads the validated P1 model
#   - validates required features
#   - generates model scores
#
# It does NOT:
#   - create risk levels
#   - combine P1 with P2
#   - generate alerts
#   - claim calibrated probability
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
    / "p1_ground_failure_model_slope_pga.joblib"
)


# ============================================================
# REQUIRED FEATURES
# ============================================================

REQUIRED_FEATURES = [

    "slope_degrees",

    "PGA_g"

]


# ============================================================
# MODULE METADATA
# ============================================================

MODULE_ID = "P1"

MODULE_NAME = "Ground Failure"

SCORE_FIELD = "P1_ground_failure_score"

SCORE_TYPE = "uncalibrated_model_indicator"


# ============================================================
# MODEL LOADING
# ============================================================

def load_model(model_file=None):

    if model_file is None:

        model_file = DEFAULT_MODEL_FILE

    model_file = Path(model_file)

    if not model_file.exists():

        raise FileNotFoundError(
            f"P1 model file not found: {model_file}"
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
            "P1 input is missing required features: "
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

        "features": REQUIRED_FEATURES.copy(),

        "output_field": SCORE_FIELD,

        "score_type": SCORE_TYPE,

        "model_file":
            str(DEFAULT_MODEL_FILE)

    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("QUAKESHIELD â€” P1 GROUND FAILURE MODULE TEST")
    print("=" * 60)

    print()
    print(f"Module ID: {MODULE_ID}")
    print(f"Module name: {MODULE_NAME}")

    print()
    print("Required features:")

    for feature in REQUIRED_FEATURES:

        print(f"  - {feature}")

    print()
    print(f"Model file: {DEFAULT_MODEL_FILE}")

    model = load_model()

    print()
    print("Model loading: PASS")

    # Small deterministic test dataset.
    test_data = pd.DataFrame({

        "slope_degrees": [

            10.0,

            20.0,

            30.0

        ],

        "PGA_g": [

            0.10,

            0.50,

            1.00

        ]

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
    print("P1 module test: PASS")

    print("=" * 60)
