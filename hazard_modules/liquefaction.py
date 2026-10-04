
# ============================================================
# QUAKESHIELD Ã¢â‚¬â€ P2 LIQUEFACTION HAZARD MODULE
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

    "σv/σv'",
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
    print("QUAKESHIELD LIQUEFACTION MODULE")
    print("=" * 60)


