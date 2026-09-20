import { useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";
import { scenarioData as riskData } from "./scenarioData";
const fmt = (v) =>
  v === null || v === undefined || Number.isNaN(v) ? "none mapped" : `${Number(v).toFixed(2)} km`;

const oldRiskData = [
  {
    location: "Mesetas, Colombia",
    date: "2019-12-24",
    lat: 3.395,
    lon: -74.255,
    magnitude: 5.7,
    groundFailure: 0.637466,
    liquefaction: 0.665242,
    score: 0.424069,
    risk: "MEDIUM",
    explanation:
      "Moderate ground-failure probability combined with moderate liquefaction susceptibility produces a medium overall risk.",
  },
  {
    location: "Tohoku-Oki, Japan",
    date: "2011-03-11",
    lat: 38.915,
    lon: 140.735,
    magnitude: 9.1,
    groundFailure: 0.517829,
    liquefaction: 0.734410,
    score: 0.380299,
    risk: "MEDIUM",
    explanation:
      "Moderate ground-failure probability combined with elevated liquefaction susceptibility produces a medium overall risk.",
  },
  {
    location: "Maria Antonia, Puerto Rico",
    date: "2020-01-07",
    lat: 18.295,
    lon: -67.045,
    magnitude: 6.4,
    groundFailure: 0.508948,
    liquefaction: 0.746539,
    score: 0.379949,
    risk: "MEDIUM",
    explanation:
      "Moderate ground-failure probability combined with elevated liquefaction susceptibility produces a medium overall risk.",
  },
  {
    location: "Belanting, Indonesia",
    date: "2018-08-19",
    lat: -8.505,
    lon: 116.075,
    magnitude: 6.9,
    groundFailure: 0.514544,
    liquefaction: 0.596000,
    score: 0.306668,
    risk: "MEDIUM",
    explanation:
      "Moderate ground-failure probability combined with moderate liquefaction susceptibility produces a medium overall risk.",
  },
  {
    location: "Niigata, Japan",
    date: "2004-10-23",
    lat: 37.265,
    lon: 138.785,
    magnitude: 6.6,
    groundFailure: 0.533928,
    liquefaction: 0.556208,
    score: 0.296975,
    risk: "LOW",
    explanation:
      "The combined scenario risk remains below the medium-risk threshold.",
  },
  {
    location: "Kashmir, Pakistan",
    date: "2005-10-08",
    lat: 34.265,
    lon: 73.295,
    magnitude: 7.6,
    groundFailure: 0.590240,
    liquefaction: 0.483211,
    score: 0.285210,
    risk: "LOW",
    explanation:
      "The combined scenario risk remains below the medium-risk threshold.",
  },
  {
    location: "Kobe, Japan",
    date: "1995-01-16",
    lat: 34.645,
    lon: 135.105,
    magnitude: 6.9,
    groundFailure: 0.455477,
    liquefaction: 0.596000,
    score: 0.271464,
    risk: "LOW",
    explanation:
      "The combined scenario risk remains below the medium-risk threshold.",
  },
  {
    location: "Palu, Indonesia",
    date: "2018-09-28",
    lat: -0.795,
    lon: 119.695,
    magnitude: 7.5,
    groundFailure: 0.485646,
    liquefaction: 0.443944,
    score: 0.215599,
    risk: "LOW",
    explanation:
      "The combined scenario risk remains below the medium-risk threshold.",
  },
  {
    location: "Tari, Papua New Guinea",
    date: "2018-02-25",
    lat: -5.595,
    lon: 141.985,
    magnitude: 7.5,
    groundFailure: 0.474084,
    liquefaction: 0.443944,
    score: 0.210467,
    risk: "LOW",
    explanation:
      "The combined scenario risk remains below the medium-risk threshold.",
  },
];

function getRiskClass(risk) {
  if (risk === "HIGH") return "high";
  if (risk === "MEDIUM") return "medium";
  return "low";
}

function getMarkerColor(risk) {
  if (risk === "HIGH") return "#ff4655";
  if (risk === "MEDIUM") return "#ffad3d";
  return "#39ce76";
}

function App() {
  const [selected, setSelected] = useState(riskData[0]);

  const highCount = riskData.filter(
    (item) => item.risk === "HIGH"
  ).length;

  const mediumCount = riskData.filter(
    (item) => item.risk === "MEDIUM"
  ).length;

  const lowCount = riskData.filter(
    (item) => item.risk === "LOW"
  ).length;

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">
        <div>
          <h1>QuakeShield</h1>
          <p>
            Earthquake-triggered cascading hazard risk assessment
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Active
        </div>
      </header>

      {/* DASHBOARD STATS */}
      <section className="stats">

        <div className="stat-card">
          <div className="stat-label">
            EARTHQUAKE SCENARIOS
          </div>
          <div className="stat-value">
            {riskData.length}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">
            HIGH RISK
          </div>
          <div className="stat-value high-text">
            {highCount}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">
            MEDIUM RISK
          </div>
          <div className="stat-value medium-text">
            {mediumCount}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">
            LOW RISK
          </div>
          <div className="stat-value low-text">
            {lowCount}
          </div>
        </div>

      </section>

      {/* MAIN CONTENT */}
      <main className="main">

        {/* MAP */}
        <section className="map-card">

          <div className="section-header">
            <div>
              <h2>Risk Map</h2>
              <p>
                Interactive earthquake-triggered hazard scenarios
              </p>
            </div>

            <div className="legend">
              <div>
                <span className="legend-dot high-dot"></span>
                High
              </div>

              <div>
                <span className="legend-dot medium-dot"></span>
                Medium
              </div>

              <div>
                <span className="legend-dot low-dot"></span>
                Low
              </div>
            </div>
          </div>

          <MapContainer
            center={[20, 0]}
            zoom={2}
            minZoom={2}
            className="real-map" style={{ height: 560 }}
          >

            <TileLayer attribution="Map data: OpenStreetMap contributors, SRTM | Style: OpenTopoMap (CC-BY-SA)" url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png" maxZoom={17} />

            {riskData.map((event, index) => (

              <CircleMarker
                key={index}
                center={[event.lat, event.lon]}
                radius={13}
                pathOptions={{
                  color: getMarkerColor(event.risk),
                  fillColor: getMarkerColor(event.risk),
                  fillOpacity: 0.8,
                  weight: 2,
                }}

                eventHandlers={{
                  click: () => setSelected(event),
                }}
              >

                <Popup>
                  <div className="popup">

                    <strong>{event.location}</strong>

                    <br />

                    Magnitude: {event.magnitude}

                    <br />

                    Risk:{" "}
                    <strong>{event.risk}</strong>

                    <br />

                    Score: {event.score.toFixed(3)}

                  </div>
                </Popup>

              </CircleMarker>

            ))}

          </MapContainer>

        </section>

        {/* DETAILS PANEL */}
        <section className="details-card">

          <div className="details-header">
            <div>
              <h2>Scenario Details</h2>
              <p>Selected earthquake scenario</p>
            </div>

            <span
              className={`risk-badge ${getRiskClass(
                selected.risk
              )}`}
            >
              {selected.risk}
            </span>
          </div>

          <div className="location-name">
            {selected.location}
          </div>

          <div className="details-grid">

            <div className="detail-item">
              <span>Earthquake Date</span>
              <strong>{selected.date}</strong>
            </div>

            <div className="detail-item">
              <span>Magnitude</span>
              <strong>{selected.magnitude}</strong>
            </div>

            <div className="detail-item">
              <span>Latitude</span>
              <strong>{selected.lat}</strong>
            </div>

            <div className="detail-item">
              <span>Longitude</span>
              <strong>{selected.lon}</strong>
            </div>

          </div>

          {/* MODEL OUTPUTS */}
          <div className="model-section">

            <h3>Model Outputs</h3>

            <div className="probability-row">

              <div className="probability-card">
                <span>Ground Failure</span>

                <strong>
                  {(selected.groundFailure * 100).toFixed(1)}%
                </strong>

                <div className="progress">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${selected.groundFailure * 100}%`,
                    }}
                  ></div>
                </div>

              </div>

              <div className="probability-card">
                <span>Liquefaction</span>

                <strong>
                  {(selected.liquefaction * 100).toFixed(1)}%
                </strong>

                <div className="progress">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${selected.liquefaction * 100}%`,
                    }}
                  ></div>
                </div>

              </div>

            </div>

          </div>

          {/* FINAL SCORE */}
          <div className="score-box">

            <div>
              <span>Final Risk Score</span>

              <strong>
                {selected.score.toFixed(3)}
              </strong>
            </div>

            <div className="score-description">
              Combined cascading-hazard
              risk indicator
            </div>

          </div>

          {selected.hospitalKm !== undefined && (
  <div className="explanation">
    <h3>Infrastructure Context (OpenStreetMap, within 10 km)</h3>
    <p>
      Nearest mapped: hospital {fmt(selected.hospitalKm)} · school {fmt(selected.schoolKm)} · bridge {fmt(selected.bridgeKm)} · major road {fmt(selected.roadKm)}
    </p>
    {selected.priority && <p><strong>Priority: {selected.priority}</strong></p>}
  </div>
)}
{/* EXPLANATION */}
          <div className="explanation">

            <h3>Why this risk level?</h3>

            <p>
              {selected.explanation}
            </p>

          </div>

        </section>

      </main>

      {/* PIPELINE */}
      <section className="pipeline-card">

        <h2>QuakeShield Risk Pipeline</h2>

        <div className="pipeline">

          <div className="pipeline-step">
            <span>01</span>
            <strong>Earthquake</strong>
            <small>Scenario input</small>
          </div>

          <div className="arrow">→</div>

          <div className="pipeline-step">
            <span>02</span>
            <strong>P1 Model</strong>
            <small>Ground failure</small>
          </div>

          <div className="arrow">→</div>

          <div className="pipeline-step">
            <span>03</span>
            <strong>P2 Model</strong>
            <small>Liquefaction</small>
          </div>

          <div className="arrow">→</div>

          <div className="pipeline-step">
            <span>04</span>
            <strong>Risk Fusion</strong>
            <small>Combined score</small>
          </div>

          <div className="arrow">→</div>

          <div className="pipeline-step">
            <span>05</span>
            <strong>Decision</strong>
            <small>Risk level + priority</small>
          </div>

        </div>

      </section>

      {/* FOOTER */}
      <footer>
        QuakeShield • Earthquake-triggered cascading hazard risk assessment
      </footer>

    </div>
  );
}

export default App;