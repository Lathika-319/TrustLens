# ============================================================
# QUAKESHIELD — HAZARD ARCHITECTURE VALIDATOR
# ============================================================
#
# Checks consistency between:
#   1. Hazard registry
#   2. Production pipeline configuration
#   3. Production output
#
# This script does NOT modify models or pipeline outputs.
# ============================================================

from pathlib import Path
import pandas as pd

from hazard_registry import (
    get_active_hazard_modules,
    get_context_modules,
    validate_registry
)


PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# EXPECTED PRODUCTION CONFIGURATION
# ============================================================

EXPECTED_P1_MODEL = (
    PROJECT_ROOT
    / "models"
    / "p1_ground_failure_model_slope_pga.joblib"
)

EXPECTED_P2_MODEL = (
    PROJECT_ROOT
    / "models"
    / "p2_liquefaction_model.joblib"
)

FINAL_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "quakeshield_final_output.csv"
)


# ============================================================
# VALIDATE REGISTRY
# ============================================================

def check_registry():

    errors = validate_registry()

    if errors:

        print("Registry validation: FAILED")

        for error in errors:
            print(f"  ERROR: {error}")

        return False

    print("Registry validation: PASS")

    return True


# ============================================================
# VALIDATE MODEL FILES
# ============================================================

def check_model_files():

    passed = True

    print()
    print("Model file checks")
    print("-" * 60)

    for module in get_active_hazard_modules():

        model_file = (
            PROJECT_ROOT
            / module["model_file"]
        )

        if model_file.exists():

            print(
                f"{module['id']} model file: PASS"
                f" -> {module['model_file']}"
            )

        else:

            print(
                f"{module['id']} model file: FAIL"
                f" -> {module['model_file']}"
            )

            passed = False

    return passed


# ============================================================
# VALIDATE EXPECTED P1/P2 MODELS
# ============================================================

def check_expected_models():

    passed = True

    print()
    print("Production model checks")
    print("-" * 60)

    if EXPECTED_P1_MODEL.exists():

        print(
            "P1 production model: PASS"
        )

    else:

        print(
            "P1 production model: FAIL"
        )

        passed = False

    if EXPECTED_P2_MODEL.exists():

        print(
            "P2 production model: PASS"
        )

    else:

        print(
            "P2 production model: FAIL"
        )

        passed = False

    return passed


# ============================================================
# VALIDATE FINAL OUTPUT
# ============================================================

def check_final_output():

    print()
    print("Production output checks")
    print("-" * 60)

    if not FINAL_OUTPUT.exists():

        print(
            "Final output file: FAIL"
            " — file does not exist"
        )

        return False

    data = pd.read_csv(FINAL_OUTPUT)

    print(
        f"Final output file: PASS"
        f" — {len(data):,} rows"
    )

    required_columns = [

        "location_name",

        "P1_ground_failure_score",

        "mean_P2_liquefaction_model_score",

        "spatial_evidence_available",

        "infrastructure_count",

        "review_context"

    ]

    passed = True

    for column in required_columns:

        if column in data.columns:

            print(
                f"Column {column}: PASS"
            )

        else:

            print(
                f"Column {column}: FAIL"
            )

            passed = False

    forbidden_columns = [

        "risk_level",

        "final_risk_score"

    ]

    for column in forbidden_columns:

        if column in data.columns:

            print(
                f"Forbidden column {column}: FAIL"
            )

            passed = False

        else:

            print(
                f"Forbidden column {column}: PASS"
            )

    return passed


# ============================================================
# VALIDATE CONTEXT MODULES
# ============================================================

def check_context_modules():

    print()
    print("Context module checks")
    print("-" * 60)

    passed = True

    for module in get_context_modules():

        print(
            f"{module['id']} — "
            f"{module['name']}: PASS"
        )

    return passed


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():

    print()
    print("=" * 60)
    print("QUAKESHIELD HAZARD ARCHITECTURE VALIDATION")
    print("=" * 60)

    checks = [

        check_registry(),

        check_model_files(),

        check_expected_models(),

        check_final_output(),

        check_context_modules()

    ]

    print()
    print("=" * 60)

    if all(checks):

        print("ARCHITECTURE VALIDATION: PASS")

        print()
        print(
            "Registry, model files, production output "
            "and context modules are consistent."
        )

        print(
            "No combined risk score is required."
        )

    else:

        print("ARCHITECTURE VALIDATION: FAILED")

        print()
        print(
            "Review the failed checks before continuing."
        )

        raise SystemExit(1)

    print("=" * 60)


if __name__ == "__main__":

    main()