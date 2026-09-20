# QuakeShield
Earthquake-triggered cascading hazard risk assessment.

Pipeline: P1 ground failure (logistic regression) -> P2 liquefaction (gradient boosting) -> risk fusion (P1 x P2) -> LOW/MEDIUM/HIGH -> OpenStreetMap infrastructure context -> response priority.

## Run
python quakeshield_pipeline.py
cd frontend
npm install
python make_data2.py ..\outputs\quakeshield_final_output.csv
npm run dev

## Scope
Infrastructure context = nearest OSM-mapped hospital, school, bridge and major road within 10 km of each scenario point (proximity, not exposure). Hazard-area overlap and population exposure are planned next steps.
