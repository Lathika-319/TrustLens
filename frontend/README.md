# QuakeShield dashboard

React + Vite + Leaflet front end for QuakeShield. It shows each earthquake scenario on a terrain map with hazard probabilities, the risk score, nearby OpenStreetMap infrastructure and the response priority.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:5173.

## Data

The dashboard reads `src/scenarioData.js`, which is generated from `../outputs/quakeshield_final_output.csv`. After re-running the pipeline, regenerate it with:

```bash
python make_data2.py ../outputs/quakeshield_final_output.csv
```

## Files

- `src/App.jsx` - map, scenario details, infrastructure context panel
- `src/App.css` - styling
- `src/scenarioData.js` - generated scenario data
- `make_data2.py` - converts the pipeline CSV into `scenarioData.js`

Map tiles: OpenTopoMap (terrain), data (c) OpenStreetMap contributors, SRTM.