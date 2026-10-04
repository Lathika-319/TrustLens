# QUAKESHIELD

## Hazard Intelligence for Earthquake-Triggered Secondary Hazards

QuakeShield is a prototype decision-support system for screening **co-seismic secondary hazards** associated with historical earthquake scenarios.

The current system combines:

* Earthquake scenario information
* **P1 — Ground-failure model indicator**
* **P2 — Liquefaction model indicator**
* Verified historical and ShakeMap spatial evidence
* Mapped infrastructure context
* Human-review guidance

The system is designed to help a reviewer understand **where secondary-hazard evidence exists and what supporting information is available**.

> **Important:** The current prototype is not a real-time earthquake warning system, does not predict future earthquakes, does not issue automatic public alerts, and does not produce a single combined probability of overall risk.

---

# 1. Problem

A major earthquake can trigger multiple secondary hazards, including:

* Ground failure
* Liquefaction
* Landslides
* Lateral spreading
* Other site-specific ground effects

A single earthquake can therefore require examination from several hazard perspectives.

Traditional workflows may require different datasets, models, spatial evidence sources, and infrastructure information to be reviewed separately.

QuakeShield explores a modular architecture where individual hazard indicators and supporting evidence can be presented together for human review.

---

# 2. Current Objective

The current prototype focuses on:

1. Screening ground-failure behavior using earthquake-aware information.
2. Screening liquefaction susceptibility using geotechnical information.
3. Connecting selected historical earthquake scenarios with verified spatial evidence.
4. Providing mapped infrastructure context.
5. Keeping different hazard indicators separate rather than forcing them into an unsupported combined risk score.
6. Supporting human interpretation rather than replacing expert or authority decisions.

---

# 3. Current System Scope

The current implementation uses **historical earthquake scenarios**.

It should therefore be understood as:

> **Historical co-seismic secondary-hazard screening and evidence review.**

It is **not** currently:

* A real-time earthquake detection system
* A future-earthquake prediction system
* A calibrated probability-of-damage system
* A public warning system
* A verified damage assessment system
* An exposure or vulnerability model
* An automatic evacuation recommendation system

These are potential future extensions.

---

# 4. System Architecture

```text
                    HISTORICAL EARTHQUAKE SCENARIO
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Scenario Information   │
                    │ Magnitude / Location    │
                    │ Date / Depth / PGA      │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐
      │ P1 Ground     │  │ P2 Liquefaction│  │ Spatial Evidence │
      │ Failure       │  │               │  │                  │
      │ Indicator     │  │ Indicator     │  │ Historical cases │
      │               │  │               │  │ ShakeMap PGA     │
      └───────┬───────┘  └───────┬───────┘  └────────┬─────────┘
              │                  │                   │
              └──────────────────┼───────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Infrastructure Context │
                    │ Hospitals / Schools     │
                    │ Bridges / Roads         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Human Review Support    │
                    │ Evidence + Indicators   │
                    │ Context + Explanation   │
                    └─────────────────────────┘
```

The architecture intentionally keeps the hazard indicators separate.

There is **no primary combined risk score** in the current production system.

---

# 5. Hazard Modules

## P1 — Ground Failure

### Status

**ACTIVE**

### Production model

```text
models/p1_ground_failure_model_slope_pga.joblib
```

### Production dataset

```text
data/QuakeShield_Final_Dataset_Slope_PGA.csv
```

### Features

* `slope_degrees`
* `PGA_g`

The model uses:

```text
Median Imputation
        ↓
StandardScaler
        ↓
LogisticRegression
```

### Dataset

The production dataset contains:

* 12,360 rows
* 9 earthquake scenarios
* 6,283 landslide-labelled observations
* 6,077 background observations

All rows have strong mapping confidence in the prepared dataset.

### Validation

Leave-One-Earthquake-Out (LOEO) evaluation produced:

```text
Mean ROC-AUC = 0.7177
```

A within-earthquake permutation diagnostic using 100 permutations produced:

```text
Observed LOEO AUC : 0.7177
Permutation mean  : 0.5001
Permutation SD    : 0.0107
Maximum null AUC  : 0.5246
Permutations >= observed : 0 / 100
Empirical p-value : 0.0099
```

This diagnostic supports that the observed model performance was not reproduced by the tested within-earthquake permutation null.

It does **not** prove causality, calibrated probability, or universal future generalization.

### Interpretation

The P1 output is a **model indicator/score**.

It should not be interpreted as a calibrated probability of landslide occurrence.

---

# 6. P2 — Liquefaction

### Status

**ACTIVE**

### Production model

```text
models/p2_liquefaction_model.joblib
```

### Training data

```text
data/raw/Database 7.xlsx
```

The `Liq database` worksheet contains the training data.

### Model

The production model uses:

```text
SimpleImputer
      ↓
GradientBoostingClassifier
```

### Features

The model uses geotechnical and earthquake-related variables including:

* Effective stress ratio
* `(N1)60`
* `qt1N`
* `Ic`
* `VS1`
* Fines content
* Depth
* Magnitude
* PGA

Missingness indicators are also retained for selected geotechnical variables.

### Important limitation

The P2 training workbook does not contain geographic coordinates.

Therefore, the current P2 model is a **magnitude-conditioned geotechnical model indicator**, not a fully event-specific spatial liquefaction map.

Scenario-level P2 values should therefore not be interpreted as calibrated event-level liquefaction probabilities.

---

# 7. Spatial Evidence

### Status

**ACTIVE CONTEXT MODULE**

Spatial evidence provides additional historical and ground-motion context for selected earthquake scenarios.

The current evidence layer combines:

* Verified historical liquefaction records
* Next Generation Liquefaction (NGL) mapped anchors
* Historical PGA observations
* USGS ShakeMap PGA at verified anchors

### Current verified scenarios

Spatial evidence is currently available for:

* Tohoku-Oki
* Kobe
* Niigata-Chuetsu

### Example evidence

For Tohoku-Oki:

```text
Verified anchors: 5
Historical records: 18
Mean historical liquefaction rate: 82.9%
Mean ShakeMap PGA: 0.371 g
```

For Kobe:

```text
Verified anchors: 3
Historical records: 55
Mean historical liquefaction rate: 66.7%
Mean ShakeMap PGA: 0.708 g
```

For Niigata-Chuetsu:

```text
Verified anchors: 3
Historical records: 3
Mean historical liquefaction rate: 33.3%
Mean ShakeMap PGA: 0.101 g
```

These values are presented as **historical and spatial evidence**, not as predictions or calibrated probabilities.

### Important design decision

A heuristic single spatial score was investigated and rejected.

The final architecture preserves:

* Historical evidence
* ShakeMap evidence
* Anchor count
* Historical outcome information

as separate evidence fields.

---

# 8. Infrastructure Context

### Status

**ACTIVE CONTEXT MODULE**

Infrastructure information is retrieved as geographic context around a representative scenario location.

Current categories include:

* Hospitals
* Schools
* Bridges
* Roads

The infrastructure query uses a 10 km geographic search area.

### Important limitation

The current infrastructure location is based on a **representative scenario dataset cell**, not necessarily a verified earthquake epicenter.

Therefore the system should describe this information as:

> **Mapped infrastructure proximity context within 10 km of the representative scenario location.**

It should not be described as:

* Confirmed exposed infrastructure
* Vulnerable infrastructure
* Damaged infrastructure
* Infrastructure at risk
* Predicted infrastructure impact

A zero count means that no mapped features were returned by the query; it does not prove that the category is absent.

---

# 9. Why There Is No Combined Risk Score

Earlier versions of the prototype multiplied the P1 and P2 outputs:

```text
P1 × P2
```

and converted the result into:

```text
HIGH / MEDIUM / LOW
```

This approach was removed.

The multiplication was a design heuristic rather than a validated probabilistic fusion method.

The P1 and P2 models also represent different hazard mechanisms and are based on different datasets.

Therefore the production system now reports:

```text
P1 Ground-Failure Indicator
              +
P2 Liquefaction Indicator
              +
Spatial Evidence
              +
Infrastructure Context
```

rather than:

```text
Single Combined Risk Score
```

This prevents the dashboard from presenting an unsupported number as an overall probability or risk level.

---

# 10. Human-in-the-Loop Design

QuakeShield is designed as a **decision-support prototype**.

The system provides:

* Model indicators
* Historical evidence
* Spatial evidence
* Infrastructure context
* Supporting explanations

A human reviewer remains responsible for interpreting the evidence.

The current prototype does not automatically:

* Issue warnings
* Order evacuations
* Declare an area unsafe
* Confirm damage
* Approve emergency actions

---

# 11. Modular Hazard Architecture

The project uses a registry-based architecture.

```text
hazard_registry.py
        │
        ├── P1 Ground Failure
        │       └── ACTIVE
        │
        ├── P2 Liquefaction
        │       └── ACTIVE
        │
        ├── P3 Landslide
        │       └── PLANNED
        │
        ├── P4 Lateral Spreading
        │       └── PLANNED / EVALUATED
        │
        ├── E1 Spatial Evidence
        │       └── ACTIVE
        │
        └── C1 Infrastructure Context
                └── ACTIVE
```

The architecture allows additional hazard modules to be evaluated independently before being promoted to production.

---

# 12. P4 — Lateral Spreading Research Evaluation

Lateral spreading was investigated using Next Generation Liquefaction field observations.

### Research status

**EVALUATED — NOT PROMOTED**

A leakage-safe research dataset was constructed.

Final dataset:

```text
299 clean field observations
36 earthquake event groups
37 positive observations
262 negative observations
```

Feature coverage:

```text
PGA              100%
PGV               99%
Arias Intensity   99%
```

Outcome/displacement variables were not used as predictors.

### Candidate predictors

* PGA
* PGV
* Arias Intensity

### Validation

Leave-One-Earthquake-Out evaluation:

```text
ROC-AUC = 0.5362
PR-AUC  = 0.1286
```

A 100-permutation within-earthquake diagnostic produced:

```text
Observed AUC       : 0.5362
Permutation mean   : 0.5377
Permutation SD     : 0.0676
95th percentile    : 0.6311
Permutations >= observed : 57 / 100
Empirical p-value  : 0.5743
```

### Decision

The observed P4 performance was not distinguishable from the tested permutation null.

Therefore:

* P4 is not promoted to production.
* P4 is not connected to the active registry.
* P4 is not connected to the production pipeline.
* P4 is not displayed as an operational hazard indicator.

The research dataset, candidate model, and validation results are retained for reproducibility and future investigation.

This rejection means that the tested model was insufficient for production; it does not mean that lateral spreading is unimportant.

---

# 13. Production Pipeline

Main pipeline:

```text
quakeshield_pipeline.py
```

The pipeline loads active hazard modules through the hazard registry.

```text
Historical Scenario
        │
        ├── P1 module
        │     └── Ground-failure score
        │
        ├── P2 module
        │     └── Liquefaction score
        │
        ├── E1 module
        │     └── Spatial evidence
        │
        └── C1 module
              └── Infrastructure context
                    │
                    ▼
              Final scenario output
```

---

# 14. Production Outputs

The main production outputs include:

```text
outputs/quakeshield_final_output.csv
outputs/quakeshield_map_data.csv
outputs/quakeshield_explanations.csv
outputs/p2_review_context.csv
outputs/p2_spatial_evidence_final.csv
```

The final production output contains separate indicators and context fields.

Important production fields include:

```text
location_name
P1_ground_failure_score
mean_P2_liquefaction_model_score
spatial_evidence_available
spatial_anchor_count
spatial_historical_records
spatial_mean_ShakeMap_PGA
spatial_mean_historical_L_rate
infrastructure_count
review_context
```

The production output intentionally does not require:

```text
risk_level
final_risk_score
```

---

# 15. Frontend

The dashboard is implemented using React/Vite.

Location:

```text
frontend/
```

The frontend presents:

* Historical earthquake scenarios
* P1 indicator
* P2 indicator
* Spatial evidence
* Infrastructure context
* Review guidance
* System status
* Scenario explanations

The dashboard does not present a combined risk score or automatic alert.

---

# 16. Decision Pipeline

The current conceptual decision pipeline is:

```text
USGS / Historical Earthquake Data
             │
             ▼
     Earthquake Scenario
             │
      ┌──────┴──────┐
      ▼             ▼
 P1 Ground       P2 Liquefaction
 Failure         Indicator
 Indicator
      │             │
      └──────┬──────┘
             │
             ▼
     Spatial Evidence
             │
             ▼
 Infrastructure Context
             │
             ▼
      Human Review
```

The output is intended to support investigation, not automatically make an emergency decision.

---

# 17. Validation

Architecture validation is performed using:

```text
validate_hazard_architecture.py
```

The validation checks:

* Hazard registry consistency
* Active model files
* Production P1 model
* Production P2 model
* Production output structure
* Required columns
* Forbidden legacy risk fields
* Spatial evidence context module
* Infrastructure context module

Current validation status:

```text
Registry validation: PASS
P1 model file: PASS
P2 model file: PASS
P1 production model: PASS
P2 production model: PASS
Final output: PASS — 9 scenarios
Spatial Evidence: PASS
Infrastructure Context: PASS
Forbidden risk_level: PASS
Forbidden final_risk_score: PASS

ARCHITECTURE VALIDATION: PASS
```

---

# 18. Implemented vs Future

## Implemented

* Historical earthquake scenarios
* P1 ground-failure model
* Earthquake-aware P1 using slope + PGA
* P1 LOEO validation
* P1 permutation diagnostic
* P2 liquefaction model
* P2 geotechnical model evaluation
* Verified spatial evidence
* USGS ShakeMap PGA context
* Infrastructure mapping context
* Modular hazard registry
* Independent P1/P2 hazard modules
* Architecture validation
* React dashboard
* Human-review context
* P4 research evaluation and rejection

## Future

### Phase 5 — Dynamic Post-Earthquake Intelligence

Potential extensions include:

* Real earthquake feeds
* Post-event environmental data
* Satellite imagery/change detection
* Soil and moisture information
* Rainfall/weather context
* Ground/seismic observations
* Dynamic reassessment

### Phase 6 — Authority Decision Support

Potential extensions include:

* Authority dashboard
* Evidence-based location explanation
* Supporting evidence visualization
* Infrastructure context
* Human verification workflow
* Review/approve/reject workflow

### Phase 7 — Public Precaution System

Potential extensions include:

* Authority-approved alerts
* Location-specific precautions
* Individual notifications
* Official-information integration
* False-positive safeguards
* False-negative safeguards

These capabilities are **future architecture**, not current implemented functionality.

---

# 19. Important Scientific Limitations

The current prototype has several limitations.

### P1

The prepared background observations are not confirmed unaffected locations.

The P1 score is not a calibrated probability.

The model is validated on historical earthquake scenarios and should not automatically be interpreted as universally predictive.

### P2

The training database does not contain coordinates.

The current P2 model is therefore not a complete spatial event-specific liquefaction model.

Magnitude-based scenario mapping can produce repeated site usage and should be interpreted cautiously.

### Spatial Evidence

Spatial evidence exists only for selected historical scenarios.

One-record historical cases provide contextual evidence rather than strong statistical support.

Historical evidence is not automatically transferable to every future earthquake.

### Infrastructure

Infrastructure data represents mapped geographic context.

The current system does not estimate structural vulnerability, damage, casualties, or economic loss.

### Overall System

The current prototype does not provide a validated unified risk probability.

Human interpretation remains necessary.

---

# 20. Repository Structure

```text
TrustLens-push/
│
├── HAZARD_ARCHITECTURE.md
├── README.md
├── quakeshield_pipeline.py
├── hazard_registry.py
├── validate_hazard_architecture.py
├── connect_hazard_modules.py
│
├── hazard_modules/
│   ├── ground_failure.py
│   └── liquefaction.py
│
├── models/
│   ├── p1_ground_failure_model_slope_pga.joblib
│   └── p2_liquefaction_model.joblib
│
├── data/
│   ├── QuakeShield_Final_Dataset_Slope_PGA.csv
│   └── raw/
│
├── scripts/
│   ├── p1/
│   └── p2/
│
├── outputs/
│
└── frontend/
    ├── src/
    ├── package.json
    └── ...
```

Research artifacts and validation outputs are retained to support reproducibility.

---

# 21. Reproducibility

The project retains:

* Dataset preparation scripts
* Model training scripts
* LOEO validation scripts
* Permutation diagnostics
* Spatial evidence processing
* NGL investigation artifacts
* Architecture validation
* Hazard module equivalence tests

This allows the current production architecture and rejected research experiments to be reviewed independently.

---

# 22. Project Status

```text
QUAKESHIELD
────────────────────────────────────────────

P1 Ground Failure          ACTIVE       ✓
P2 Liquefaction            ACTIVE       ✓
E1 Spatial Evidence        ACTIVE       ✓
C1 Infrastructure Context  ACTIVE       ✓

P3 Landslide               PLANNED      —
P4 Lateral Spreading       EVALUATED    REJECTED

Combined Risk Score        REMOVED      ✓
Risk Levels                REMOVED      ✓
Automatic Alerts           NOT ACTIVE   ✓
Human Review               REQUIRED     ✓

Architecture Validation    PASS         ✓
```

---

# 23. Final System Definition

> **QuakeShield is a modular prototype for screening co-seismic secondary hazards in historical earthquake scenarios. It combines separate ground-failure and liquefaction model indicators with verified spatial evidence and mapped infrastructure context to support human review.**

The architecture is intentionally designed so that future hazard modules and dynamic data sources can be added only after independent validation.

---

## Disclaimer

QuakeShield is a research/prototype decision-support system.

Its outputs should not be used as a substitute for official earthquake information, engineering assessment, emergency-management procedures, or decisions by qualified authorities.
