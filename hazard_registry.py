
# ============================================================
# QUAKESHIELD — HAZARD MODULE REGISTRY
# ============================================================
#
# Central registry for independent hazard modules.
#
# IMPORTANT:
# This registry describes the modules and their interpretation.
# It does NOT combine their scores into a single risk score.
# ============================================================


# ============================================================
# P1 — GROUND FAILURE
# ============================================================

P1_GROUND_FAILURE = {

    "id": "P1",

    "name": "Ground Failure",

    "short_name": "Ground Failure",

    "status": "active",

    "model_file":
        r"models\p1_ground_failure_model_slope_pga.joblib",

    "dataset_file":
        r"data\QuakeShield_Final_Dataset_Slope_PGA.csv",

    "features": [

        "slope_degrees",

        "PGA_g"

    ],

    "output_field":
        "P1_ground_failure_score",

    "score_type":
        "uncalibrated_model_indicator",

    "description":
        "Ground-failure model indicator based on slope and PGA.",

    "limitations": [

        "Score is not a calibrated probability.",

        "Background cells are not confirmed unaffected.",

        "Prepared dataset contains sampling structure.",

        "Results do not establish universal future-event performance.",

        "PGA association should not be interpreted as causal proof."

    ]

}


# ============================================================
# P2 — LIQUEFACTION
# ============================================================

P2_LIQUEFACTION = {

    "id": "P2",

    "name": "Liquefaction",

    "short_name": "Liquefaction",

    "status": "active",

    "model_file":
        r"models\p2_liquefaction_model.joblib",

    "dataset_file":
        r"data\raw\Database 7.xlsx",

    "features": [

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

    ],

    "output_field":
        "P2_liquefaction_model_score",

    "score_type":
        "uncalibrated_model_indicator",

    "description":
        "Liquefaction model indicator based on geotechnical variables, earthquake magnitude and PGA.",

    "limitations": [

        "Score is not a calibrated probability.",

        "Current scenario mapping uses nearest available magnitude.",

        "P2 training sites are not co-located with P1 grid cells.",

        "Current implementation is not an event-specific spatial liquefaction map.",

        "Spatial evidence is therefore maintained separately."

    ]

}


# ============================================================
# FUTURE MODULE PLACEHOLDERS
# ============================================================

P3_LANDSLIDE = {

    "id": "P3",

    "name": "Landslide",

    "short_name": "Landslide",

    "status": "planned",

    "model_file": None,

    "dataset_file": None,

    "features": [],

    "output_field":
        "P3_landslide_score",

    "score_type":
        "not_implemented",

    "description":
        "Future earthquake-triggered landslide hazard module.",

    "limitations": [

        "Not implemented.",

        "No model has been validated.",

        "No score should be displayed."

    ]

}


P4_LATERAL_SPREADING = {

    "id": "P4",

    "name": "Lateral Spreading",

    "short_name": "Lateral Spreading",

    "status": "planned",

    "model_file": None,

    "dataset_file": None,

    "features": [],

    "output_field":
        "P4_lateral_spreading_score",

    "score_type":
        "not_implemented",

    "description":
        "Future lateral-spreading hazard module.",

    "limitations": [

        "Not implemented.",

        "No model has been validated.",

        "No score should be displayed."

    ]

}


# ============================================================
# SPATIAL EVIDENCE MODULE
# ============================================================

SPATIAL_EVIDENCE = {

    "id": "E1",

    "name": "Spatial Evidence",

    "short_name": "Spatial Evidence",

    "status": "active",

    "output_fields": [

        "spatial_evidence_available",

        "spatial_anchor_count",

        "spatial_historical_records",

        "spatial_mean_ShakeMap_PGA",

        "spatial_mean_historical_L_rate"

    ],

    "description":
        "Verified historical cases, mapped anchors and ShakeMap context.",

    "score_type":
        "evidence_context",

    "limitations": [

        "Evidence availability varies by scenario.",

        "Historical records do not represent complete event coverage.",

        "Single-record historical cases are contextual only.",

        "Evidence is not converted into a universal risk score."

    ]

}


# ============================================================
# INFRASTRUCTURE CONTEXT MODULE
# ============================================================

INFRASTRUCTURE_CONTEXT = {

    "id": "C1",

    "name": "Infrastructure Context",

    "short_name": "Infrastructure",

    "status": "active",

    "output_fields": [

        "infrastructure_count",

        "nearest_infrastructure_distance_km",

        "hospital_count",

        "school_count",

        "bridge_count",

        "road_count"

    ],

    "description":
        "Mapped infrastructure proximity context around representative scenario locations.",

    "score_type":
        "geographic_context",

    "limitations": [

        "Query is centered on a representative scenario location.",

        "It is not a verified exposure assessment.",

        "It is not a vulnerability assessment.",

        "It is not a damage assessment.",

        "Zero returned features does not prove infrastructure absence."

    ]

}


# ============================================================
# ACTIVE MODULES
# ============================================================

ACTIVE_HAZARD_MODULES = [

    P1_GROUND_FAILURE,

    P2_LIQUEFACTION

]


# ============================================================
# PLANNED MODULES
# ============================================================

PLANNED_HAZARD_MODULES = [

    P3_LANDSLIDE,

    P4_LATERAL_SPREADING

]


# ============================================================
# CONTEXT MODULES
# ============================================================

CONTEXT_MODULES = [

    SPATIAL_EVIDENCE,

    INFRASTRUCTURE_CONTEXT

]


# ============================================================
# ALL MODULES
# ============================================================

ALL_MODULES = (

    ACTIVE_HAZARD_MODULES

    +

    PLANNED_HAZARD_MODULES

    +

    CONTEXT_MODULES

)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_active_hazard_modules():

    return ACTIVE_HAZARD_MODULES.copy()


def get_planned_hazard_modules():

    return PLANNED_HAZARD_MODULES.copy()


def get_context_modules():

    return CONTEXT_MODULES.copy()


def get_module(module_id):

    for module in ALL_MODULES:

        if module["id"] == module_id:

            return module

    return None


def print_registry():

    print()
    print("=" * 60)
    print("QUAKESHIELD HAZARD MODULE REGISTRY")
    print("=" * 60)

    print()
    print("ACTIVE HAZARD MODULES")

    for module in ACTIVE_HAZARD_MODULES:

        print(
            f"  {module['id']} — "
            f"{module['name']} "
            f"[{module['status']}]"
        )

    print()
    print("PLANNED HAZARD MODULES")

    for module in PLANNED_HAZARD_MODULES:

        print(
            f"  {module['id']} — "
            f"{module['name']} "
            f"[{module['status']}]"
        )

    print()
    print("CONTEXT MODULES")

    for module in CONTEXT_MODULES:

        print(
            f"  {module['id']} — "
            f"{module['name']} "
            f"[{module['status']}]"
        )

    print()
    print("=" * 60)


# ============================================================
# DIRECT EXECUTION
# ============================================================

# ============================================================
# REGISTRY VALIDATION
# ============================================================

def validate_registry():

    errors = []

    # Check active hazard modules
    for module in ACTIVE_HAZARD_MODULES:

        if not module.get("id"):
            errors.append("Active module missing id.")

        if not module.get("name"):
            errors.append(
                f"{module.get('id', 'UNKNOWN')} missing name."
            )

        if not module.get("model_file"):
            errors.append(
                f"{module.get('id', 'UNKNOWN')} missing model file."
            )

        if not module.get("features"):
            errors.append(
                f"{module.get('id', 'UNKNOWN')} missing features."
            )

        if not module.get("output_field"):
            errors.append(
                f"{module.get('id', 'UNKNOWN')} missing output field."
            )

    # Check duplicate IDs
    ids = [module["id"] for module in ALL_MODULES]

    duplicates = {
        module_id
        for module_id in ids
        if ids.count(module_id) > 1
    }

    if duplicates:

        errors.append(
            "Duplicate module IDs: "
            + ", ".join(sorted(duplicates))
        )

    # Check that active and planned modules are not duplicated
    active_ids = {
        module["id"]
        for module in ACTIVE_HAZARD_MODULES
    }

    planned_ids = {
        module["id"]
        for module in PLANNED_HAZARD_MODULES
    }

    overlap = active_ids.intersection(planned_ids)

    if overlap:

        errors.append(
            "Module appears in both active and planned: "
            + ", ".join(sorted(overlap))
        )

    return errors


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    print_registry()

    print()
    print("REGISTRY VALIDATION")
    print("-" * 60)

    validation_errors = validate_registry()

    if validation_errors:

        print("STATUS: FAILED")

        for error in validation_errors:

            print(f"  ERROR: {error}")

        raise SystemExit(1)

    else:

        print("STATUS: PASSED")
        print("All registry checks passed.")
