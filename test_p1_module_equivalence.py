# ============================================================
# QUAKESHIELD — P1 MODULE EQUIVALENCE TEST
# ============================================================
#
# Verifies that the independent P1 module produces the same
# scenario-level scores as the current production output.
#
# No files are modified.
# ============================================================

from pathlib import Path

import pandas as pd

from hazard_modules.ground_failure import (
    load_model,
    predict_scores
)


PROJECT_ROOT = Path(__file__).resolve().parent

P1_DATASET = (
    PROJECT_ROOT
    / "data"
    / "QuakeShield_Final_Dataset_Slope_PGA.csv"
)

FINAL_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "quakeshield_final_output.csv"
)


DATASET_SCENARIO_COLUMN = "earthquake_name"

OUTPUT_SCENARIO_COLUMN = "location_name"

P1_OUTPUT_COLUMN = "P1_ground_failure_score"


# ============================================================
# START
# ============================================================

print()
print("=" * 60)
print("QUAKESHIELD — P1 MODULE EQUIVALENCE TEST")
print("=" * 60)


# ============================================================
# LOAD P1 DATASET
# ============================================================

print()
print("Loading P1 dataset...")

p1_data = pd.read_csv(P1_DATASET)

print(
    f"P1 rows: {len(p1_data):,}"
)


if DATASET_SCENARIO_COLUMN not in p1_data.columns:

    raise ValueError(
        f"Missing dataset scenario column: "
        f"{DATASET_SCENARIO_COLUMN}"
    )


# ============================================================
# LOAD MODEL
# ============================================================

model = load_model()

print("P1 model loading: PASS")


# ============================================================
# GENERATE MODULE SCORES
# ============================================================

module_scores = predict_scores(
    p1_data,
    model=model
)

p1_data["_module_score"] = module_scores


# ============================================================
# SCENARIO-LEVEL MODULE SCORES
# ============================================================

module_scenarios = (

    p1_data
    .groupby(DATASET_SCENARIO_COLUMN)["_module_score"]
    .mean()
)


# ============================================================
# LOAD PRODUCTION OUTPUT
# ============================================================

print()
print("Loading production output...")

final_output = pd.read_csv(FINAL_OUTPUT)


required_columns = [

    OUTPUT_SCENARIO_COLUMN,

    P1_OUTPUT_COLUMN

]

for column in required_columns:

    if column not in final_output.columns:

        raise ValueError(
            f"Production output missing column: {column}"
        )


# ============================================================
# SCENARIO NAME MAPPING
# ============================================================
#
# The P1 dataset uses earthquake_name.
# The final output uses location_name.
#
# We normalize both to compare them safely.
# ============================================================

def normalize_name(value):

    value = str(value).strip()

    # Dataset scenario names → final output names
    aliases = {

        "Tohoku-Oki":
            "Tohoku-Oki, Japan",

        "Belanting":
            "1 km S of Belanting, Indonesia",

        "Palu":
            "70km N of Palu, Indonesia",

        "Tari":
            "32 km SW of Tari, Papua New Guinea",

        "Mesetas":
            "9 km NW of Mesetas, Colombia",

        "Puerto Rico":
            "M 6.4 - 13 km SSE of Maria Antonia, Puerto Rico",

        "Kobe":
            "Kobe, Japan",

        "Niigata-Chuetsu":
            "Niigata-Chuetsu, Japan",

        "Kashmir":
            "Kashmir, Pakistan"

    }

    return aliases.get(
        value,
        value
    )


module_scenarios.index = (
    module_scenarios.index
    .map(normalize_name)
)


# ============================================================
# PRODUCTION SCENARIO SCORES
# ============================================================

production_scenarios = (

    final_output[
        [
            OUTPUT_SCENARIO_COLUMN,
            P1_OUTPUT_COLUMN
        ]
    ]
    .drop_duplicates(
        subset=[OUTPUT_SCENARIO_COLUMN]
    )
    .set_index(
        OUTPUT_SCENARIO_COLUMN
    )[P1_OUTPUT_COLUMN]
)


# ============================================================
# COMPARE
# ============================================================

common = (

    module_scenarios
    .index
    .intersection(
        production_scenarios.index
    )

)


print()
print("Scenario comparison")
print("-" * 60)

if len(common) == 0:

    raise RuntimeError(
        "No common scenarios found."
    )


comparison = pd.DataFrame({

    "module_score":
        module_scenarios.loc[common],

    "production_score":
        production_scenarios.loc[common]

})


comparison["absolute_difference"] = (

    comparison["module_score"]
    -
    comparison["production_score"]

).abs()


print(
    comparison.to_string()
)


# ============================================================
# VALIDATION
# ============================================================

MAX_ALLOWED_DIFFERENCE = 1e-12

max_difference = (
    comparison["absolute_difference"].max()
)


print()
print(
    f"Scenarios compared: {len(common)}"
)

print(
    f"Maximum absolute difference: "
    f"{max_difference:.15f}"
)

print(
    f"Allowed difference: "
    f"{MAX_ALLOWED_DIFFERENCE:.1e}"
)


# ============================================================
# FINAL CHECKS
# ============================================================

if len(common) != 9:

    raise SystemExit(
        "FAIL: Expected 9 common scenarios."
    )


if max_difference > MAX_ALLOWED_DIFFERENCE:

    raise SystemExit(
        "FAIL: P1 module output differs "
        "from production output."
    )


print()
print("=" * 60)
print("P1 MODULE EQUIVALENCE: PASS")
print("=" * 60)

print(
    "Independent P1 module reproduces "
    "the production P1 scenario scores."
)

print(
    "No production output differences detected."
)

print("=" * 60)