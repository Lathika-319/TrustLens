# QuakeShield
### Earthquake-triggered cascading hazard risk assessment

QuakeShield is a hackathon prototype that combines ground-failure probability, liquefaction probability and nearby OpenStreetMap infrastructure into an interpretable scenario-level risk score and a response-priority flag.



> **Prototype note:** the infrastructure layer measures proximity of OpenStreetMap-mapped features to each scenario point. It is not an exposure or damage model.

## Pipeline

```text
Earthquake scenario
  -> P1: ground-failure probability
  -> P2: liquefaction probability
  -> Risk fusion: score = P1 x P2  ->  LOW / MEDIUM / HIGH
  -> OpenStreetMap context: nearest hospital, school, bridge, major road (10 km search)
  -> Response priority + explanation
```

## Results (9 scenarios)

| Scenario | Mag | Score | Risk | Priority |
|---|---|---|---|---|
| Mesetas, Colombia | 5.7 | 0.424 | MEDIUM | PRIORITIZE - INFRASTRUCTURE NEARBY |
| Belanting, Indonesia | 6.9 | 0.382 | MEDIUM | PRIORITIZE - INFRASTRUCTURE NEARBY |
| Tohoku-Oki, Japan | 9.1 | 0.380 | MEDIUM | PRIORITIZE - INFRASTRUCTURE NEARBY |
| Maria Antonia, Puerto Rico | 6.4 | 0.380 | MEDIUM | MONITOR / FURTHER ASSESSMENT |
| Niigata-Chuetsu, Japan | 6.6 | 0.297 | LOW | LOWER PRIORITY |
| Kashmir, Pakistan | 7.6 | 0.285 | LOW | LOWER PRIORITY |
| Kobe, Japan | 6.9 | 0.271 | LOW | LOWER PRIORITY |
| Palu, Indonesia | 7.5 | 0.216 | LOW | LOWER PRIORITY |
| Tari, Papua New Guinea | 7.5 | 0.210 | LOW | LOWER PRIORITY |

Example, Belanting: ground failure 64.2%, liquefaction 59.6%, score 0.382 (MEDIUM). Nearest mapped hospital 3.15 km, school 0.75 km, bridge 0.98 km, major road 0.89 km.

## Repository layout

- `quakeshield_pipeline.py` - runs the full pipeline and writes the final output
- `scripts/p1`, `scripts/p2` - model training and evaluation
- `scripts/risk` - risk fusion, OSM infrastructure collection, explanations
- `models/` - trained P1 and P2 models
- `outputs/` - generated CSVs (final: `outputs/quakeshield_final_output.csv`)
- `frontend/` - React + Vite + Leaflet dashboard
- `data/raw/` - source datasets

## Run

Backend:

```bash
pip install -r requirements.txt
python quakeshield_pipeline.py
```

Dashboard:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dashboard reads `frontend/src/scenarioData.js`, which is generated from the pipeline output. After re-running the pipeline, regenerate it with:

```bash
python make_data2.py ../outputs/quakeshield_final_output.csv
```

Optional, to refresh the OpenStreetMap data (needs internet and osmnx):

```bash
python scripts/risk/get_infrastructure.py
python scripts/risk/calculate_infrastructure_risk.py
```

## Limitations

- Distances are measured from the scenario point, not from a hazard footprint, so this is proximity, not exposure.
- "none mapped" means OpenStreetMap returned no feature within 10 km, not that none exists in reality.
- The priority flag is a simple prototype rule: HIGH risk -> IMMEDIATE ASSESSMENT; MEDIUM with any mapped infrastructure -> PRIORITIZE; MEDIUM with none -> MONITOR; LOW -> LOWER PRIORITY. It is not a validated response-planning model.
- Population, building vulnerability and structural exposure are not included.
- Only 9 scenarios; results are not validated against real impact data.

## Future work

- Overlay infrastructure on the predicted hazard zone instead of a point radius
- Add population and building exposure
- Replace the presence-based priority rule with a distance- and exposure-aware score
- Map ground-failure and liquefaction areas directly
- Validate against historical earthquake impacts

## Disclaimer

Research prototype for demonstration. Not for operational emergency response.