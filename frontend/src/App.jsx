import React, { useMemo, useState } from "react";
import "./App.css";
import { scenarioData } from "./scenarioData";

import {
  Activity,
  Building2,
  Database,
  Gauge,
  Layers3,
  MapPin,
  Radio,
  Route,
  School,
  Shield,
  ShieldAlert,
  TrendingUp,
  Waves,
  Eye,
  EyeOff
} from "lucide-react";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap
} from "react-leaflet";

import "leaflet/dist/leaflet.css";


/* =========================================================
   DATA PREPARATION
   ========================================================= */

const scenarios = scenarioData.map(function (item, index) {
  const location =
    item.location ||
    item.location_name ||
    item.name ||
    "Unknown Scenario";

  const magnitude =
    item.magnitude ??
    item.earthquake_magnitude ??
    "";

  const date =
    item.date ||
    item.earthquake_date ||
    "";

  const latitude =
    item.lat ??
    item.latitude ??
    item.earthquake_latitude;

  const longitude =
    item.lon ??
    item.longitude ??
    item.earthquake_longitude;

  const p1 =
    item.groundFailure ??
    item.P1_ground_failure_score ??
    item.p1 ??
    0;

  const p2 =
    item.liquefaction ??
    item.mean_P2_liquefaction_model_score ??
    item.mean_P2_liquefaction_probability ??
    item.p2 ??
    0;


  /* =========================================================
     SPATIAL EVIDENCE

     scenarioData.js uses:
     spatialEvidence
     anchorCount
     historicalRecords
     meanShakeMapPGA
     historicalLRate
     ========================================================= */

  const spatialAvailable =
    item.spatialEvidence ??
    item.spatial_evidence_available ??
    item.spatialEvidenceAvailable ??
    false;


  /* =========================================================
     INFRASTRUCTURE

     scenarioData.js uses:
     infrastructureCount
     hospitalCount
     schoolCount
     bridgeCount
     roadCount
     nearestInfrastructureKm
     ========================================================= */

  const infrastructureCount =
    item.infrastructureCount ??
    item.infrastructure_count ??
    0;


  return {
    id: index + 1,

    name: location.includes(",")
      ? location.split(",")[0].trim()
      : location,

    country: location.includes(",")
      ? location.split(",").slice(1).join(",").trim()
      : "",

    location,

    magnitude,
    date,

    lat: Number(latitude),
    lon: Number(longitude),

    /* Model indicators */
    p1: Number(p1),
    p2: Number(p2),

    /* Spatial evidence */
    spatialEvidenceAvailable:
      spatialAvailable === true ||
      spatialAvailable === "True" ||
      spatialAvailable === "true",

    spatialScenario:
      item.spatialScenario ??
      item.spatial_evidence_scenario ??
      "",

    spatialAnchors: Number(
      item.anchorCount ??
      item.spatial_anchor_count ??
      item.spatialAnchorCount ??
      0
    ),

    spatialHistoricalRecords: Number(
      item.historicalRecords ??
      item.spatial_historical_records ??
      item.spatialHistoricalRecords ??
      0
    ),

    spatialMeanPGA:
      item.meanShakeMapPGA ??
      item.spatial_mean_ShakeMap_PGA ??
      item.spatialMeanShakeMapPGA ??
      null,

    spatialHistoricalRate:
      item.historicalLRate ??
      item.spatial_mean_historical_L_rate ??
      item.spatialMeanHistoricalLRate ??
      null,

    /* Infrastructure */
    infrastructureCount: Number(
      infrastructureCount
    ),

    hospitalCount: Number(
      item.hospitalCount ?? 0
    ),

    schoolCount: Number(
      item.schoolCount ?? 0
    ),

    bridgeCount: Number(
      item.bridgeCount ?? 0
    ),

    roadCount: Number(
      item.roadCount ?? 0
    ),

    nearestInfrastructureKm:
      item.nearestInfrastructureKm ??
      null,

    reviewContext:
      item.reviewContext ??
      item.review_context ??
      (
        spatialAvailable === true ||
        spatialAvailable === "True" ||
        spatialAvailable === "true"
          ? "SPATIAL EVIDENCE AVAILABLE FOR REVIEW"
          : "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE"
      ),

    explanation:
      item.explanation ||
      "Scenario evidence is presented for human review. Model scores are indicators and are not calibrated probabilities."
  };
});


/* =========================================================
   NAVIGATION
   ========================================================= */

const navItems = [
  {
    group: "MONITORING",
    items: [
      {
        id: "command",
        label: "Command Center",
        icon: Gauge
      },
      {
        id: "monitoring",
        label: "Monitoring & Review",
        icon: Radio
      }
    ]
  },

  {
    group: "ANALYSIS",
    items: [
      {
        id: "scenarios",
        label: "Hazard Scenarios",
        icon: Layers3
      },
      {
        id: "risk",
        label: "Scenario Indicators",
        icon: ShieldAlert
      }
    ]
  },

  {
    group: "CONTEXT",
    items: [
      {
        id: "infrastructure",
        label: "Infrastructure",
        icon: Building2
      }
    ]
  }
];


/* =========================================================
   HELPERS
   ========================================================= */

function score(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "0.000";
  }

  return number.toFixed(3);
}


function percentage(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  return (number * 100).toFixed(1) + "%";
}


function formatPGA(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  return number.toFixed(3) + " g";
}


function formatRate(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  return (number * 100).toFixed(1) + "%";
}


function spatialLabel(scenario) {
  return scenario.spatialEvidenceAvailable
    ? "EVIDENCE AVAILABLE"
    : "NO VERIFIED SPATIAL EVIDENCE";
}


function infrastructureLabel(count) {
  if (!Number.isFinite(Number(count))) {
    return "No mapped data";
  }

  if (Number(count) === 0) {
    return "0 mapped features";
  }

  return Number(count) + " mapped features";
}


function infrastructureCategoryLabel(count) {
  const number = Number(count);

  if (!Number.isFinite(number) || number === 0) {
    return "No mapped data";
  }

  return number + (number === 1 ? " mapped" : " mapped");
}


/* =========================================================
   MAP FOCUS
   ========================================================= */

function MapFocus({ scenario }) {
  const map = useMap();

  React.useEffect(
    function () {
      if (
        scenario &&
        Number.isFinite(scenario.lat) &&
        Number.isFinite(scenario.lon)
      ) {
        map.flyTo(
          [scenario.lat, scenario.lon],
          5,
          {
            duration: 0.8
          }
        );
      }
    },
    [scenario, map]
  );

  return null;
}


/* =========================================================
   SCENARIO MAP
   ========================================================= */

function ScenarioMap({
  scenarios,
  selectedScenario,
  onSelect
}) {
  const defaultCenter =
    selectedScenario &&
    Number.isFinite(selectedScenario.lat) &&
    Number.isFinite(selectedScenario.lon)
      ? [selectedScenario.lat, selectedScenario.lon]
      : [20, 78];

  return (
    <div className="map-card">

      <div className="section-heading">

        <div>

          <h2>
            Hazard Scenario Map
          </h2>

          <p>
            Historical earthquake scenarios and
            secondary-hazard model indicators
          </p>

        </div>

        <MapPin size={18} />

      </div>


      <div className="real-map">

        <MapContainer
          center={defaultCenter}
          zoom={3}
          scrollWheelZoom={true}
          style={{
            width: "100%",
            height: "100%"
          }}
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapFocus
            scenario={selectedScenario}
          />


          {scenarios.map(function (scenario) {

            if (
              !Number.isFinite(scenario.lat) ||
              !Number.isFinite(scenario.lon)
            ) {
              return null;
            }

            const selected =
              selectedScenario &&
              selectedScenario.id === scenario.id;

            return (
              <CircleMarker
                key={scenario.id}
                center={[
                  scenario.lat,
                  scenario.lon
                ]}
                radius={
                  selected ? 11 : 7
                }
                pathOptions={{
                  color:
                    scenario.spatialEvidenceAvailable
                      ? "#2563eb"
                      : "#64748b",

                  fillColor:
                    scenario.spatialEvidenceAvailable
                      ? "#2563eb"
                      : "#64748b",

                  fillOpacity:
                    selected ? 0.9 : 0.65,

                  weight:
                    selected ? 4 : 2
                }}
                eventHandlers={{
                  click: function () {
                    onSelect(scenario.id);
                  }
                }}
              >

                <Popup>

                  <strong>
                    {scenario.name}
                  </strong>

                  <br />

                  P1 score:{" "}
                  {score(scenario.p1)}

                  <br />

                  P2 score:{" "}
                  {score(scenario.p2)}

                  <br />

                  Spatial evidence:{" "}
                  {scenario.spatialEvidenceAvailable
                    ? "Available"
                    : "Not available"}

                  <br />

                  Magnitude:{" "}
                  {scenario.magnitude}

                </Popup>

              </CircleMarker>
            );
          })}

        </MapContainer>

      </div>


      <div className="legend">

        <div className="legend-item">

          <span
            className="legend-dot"
            style={{
              background: "#2563eb"
            }}
          />

          SPATIAL EVIDENCE AVAILABLE

        </div>


        <div className="legend-item">

          <span
            className="legend-dot"
            style={{
              background: "#64748b"
            }}
          />

          NO VERIFIED SPATIAL EVIDENCE

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   SCENARIO DETAILS
   ========================================================= */

function ScenarioDetails({
  scenario,
  monitoredId,
  onToggleMonitoring
}) {
  if (!scenario) {
    return (
      <div className="details-card">

        <div className="empty-state">

          <h2>
            No Scenario Selected
          </h2>

          <p>
            Select a scenario from the map or
            scenario register.
          </p>

        </div>

      </div>
    );
  }


  const isMonitoring =
    monitoredId === scenario.id;


  return (
    <div className="details-card">

      <div className="location-name">

        <div>

          <h2>
            {scenario.name}
          </h2>

          <div
            style={{
              marginTop: "5px",
              color: "#7b8591",
              fontSize: "11px"
            }}
          >
            {scenario.country}
          </div>

        </div>

      </div>


      <div className="details-grid">

        <div className="detail-item">

          <span>
            MAGNITUDE
          </span>

          <strong>
            {scenario.magnitude}
          </strong>

        </div>


        <div className="detail-item">

          <span>
            DATE
          </span>

          <strong>
            {scenario.date || "Historical scenario"}
          </strong>

        </div>


        <div className="detail-item">

          <span>
            LATITUDE
          </span>

          <strong>
            {Number.isFinite(scenario.lat)
              ? scenario.lat.toFixed(3)
              : "—"}
          </strong>

        </div>


        <div className="detail-item">

          <span>
            LONGITUDE
          </span>

          <strong>
            {Number.isFinite(scenario.lon)
              ? scenario.lon.toFixed(3)
              : "—"}
          </strong>

        </div>

      </div>


      {/* =====================================================
         MODEL INDICATORS
         ===================================================== */}

      <div className="probability-card">

        <div className="probability-row">

          <div>

            <span>
              P1 — GROUND-FAILURE MODEL SCORE
            </span>

            <strong>
              {score(scenario.p1)}
            </strong>

          </div>


          <div className="probability-bar">

            <div
              style={{
                width:
                  Math.min(
                    Math.max(
                      scenario.p1 * 100,
                      0
                    ),
                    100
                  ) + "%"
              }}
            />

          </div>

        </div>


        <div className="probability-row">

          <div>

            <span>
              P2 — LIQUEFACTION MODEL SCORE
            </span>

            <strong>
              {score(scenario.p2)}
            </strong>

          </div>


          <div className="probability-bar">

            <div
              style={{
                width:
                  Math.min(
                    Math.max(
                      scenario.p2 * 100,
                      0
                    ),
                    100
                  ) + "%"
              }}
            />

          </div>

        </div>

      </div>


      {/* =====================================================
         SPATIAL EVIDENCE
         ===================================================== */}

      <div className="assessment-card">

        <div className="assessment-title">

          <ShieldAlert size={15} />

          SPATIAL REVIEW CONTEXT

        </div>


        <div className="risk-score">

          <strong>
            {spatialLabel(scenario)}
          </strong>

          <span>
            Historical and ShakeMap evidence
          </span>

        </div>


        {scenario.spatialEvidenceAvailable ? (

          <div className="details-grid">

            <div className="detail-item">

              <span>
                VERIFIED ANCHORS
              </span>

              <strong>
                {scenario.spatialAnchors}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                HISTORICAL RECORDS
              </span>

              <strong>
                {scenario.spatialHistoricalRecords}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                MEAN SHAKEMAP PGA
              </span>

              <strong>
                {formatPGA(
                  scenario.spatialMeanPGA
                )}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                HISTORICAL LIQUEFACTION RATE
              </span>

              <strong>
                {formatRate(
                  scenario.spatialHistoricalRate
                )}
              </strong>

            </div>

          </div>

        ) : (

          <p className="method-note">

            No verified spatial evidence is currently
            connected to this scenario in the prototype.
            This does not imply absence of hazard.

          </p>

        )}

      </div>


      {/* =====================================================
         MODEL INTERPRETATION
         ===================================================== */}

      <div className="assessment-card">

        <div className="assessment-title">

          <Activity size={15} />

          MODEL INTERPRETATION

        </div>


        <p className="method-note">

          P1 and P2 are separate model indicators.
          They are not combined into a single probability
          or risk score. Values support comparative review
          of the current prototype scenarios.

        </p>

      </div>


      {/* =====================================================
         INFRASTRUCTURE CONTEXT
         ===================================================== */}

      <div className="assessment-card">

        <div className="assessment-title">

          <Building2 size={15} />

          INFRASTRUCTURE CONTEXT

        </div>


        <p className="method-note">

          Mapped infrastructure is shown as geographic
          context around the representative scenario
          location. It is not an exposure, vulnerability,
          damage, or safety assessment.

        </p>


        <div className="infrastructure-grid">

          <div className="infra-card">

            <span>
              HOSPITAL
            </span>

            <strong>
              {scenario.hospitalCount > 0
                ? `${scenario.hospitalCount} mapped`
                : "No mapped data"}
            </strong>

          </div>


          <div className="infra-card">

            <School size={17} />

            <span>
              SCHOOL
            </span>

            <strong>
              {scenario.schoolCount > 0
                ? `${scenario.schoolCount} mapped`
                : "No mapped data"}
            </strong>

          </div>


          <div className="infra-card">

            <Route size={17} />

            <span>
              BRIDGE
            </span>

            <strong>
              {scenario.bridgeCount > 0
                ? `${scenario.bridgeCount} mapped`
                : "No mapped data"}
            </strong>

          </div>


          <div className="infra-card">

            <Route size={17} />

            <span>
              ROAD
            </span>

            <strong>
              {scenario.roadCount > 0
                ? `${scenario.roadCount} mapped`
                : "No mapped data"}
            </strong>

          </div>

        </div>


        <p className="method-note">

          Mapped infrastructure count:{" "}

          <strong>
            {infrastructureLabel(
              scenario.infrastructureCount
            )}
          </strong>

          . Zero mapped features means no features
          were returned by the current map query.

        </p>

      </div>


      <div className="command-actions">

        <button
          className="command-primary"
          onClick={function () {
            onToggleMonitoring(
              scenario.id
            );
          }}
        >

          {isMonitoring ? (
            <>
              <EyeOff
                size={15}
                style={{
                  marginRight: "7px"
                }}
              />

              Stop Review Monitoring
            </>
          ) : (
            <>
              <Eye
                size={15}
                style={{
                  marginRight: "7px"
                }}
              />

              Monitor for Review
            </>
          )}

        </button>

      </div>


      <p className="method-note">

        {scenario.reviewContext}

      </p>

    </div>
  );
}


/* =========================================================
   PIPELINE
   ========================================================= */

function Pipeline() {

  const steps = [

    {
      icon: Database,
      title: "USGS",
      text: "Historical earthquake and hazard data"
    },

    {
      icon: TrendingUp,
      title: "P1",
      text: "Ground-failure model score"
    },

    {
      icon: Waves,
      title: "P2",
      text: "Liquefaction model score"
    },

    {
      icon: MapPin,
      title: "Spatial Evidence",
      text: "Verified historical and ShakeMap context"
    },

    {
      icon: Building2,
      title: "Infrastructure",
      text: "Mapped geographic context"
    },

    {
      icon: Shield,
      title: "Review",
      text: "Human review support"
    }

  ];


  return (
    <div className="pipeline-card">

      <div className="section-heading">

        <div>

          <h2>
            QuakeShield Decision Pipeline
          </h2>

          <p>
            From historical hazard evidence to
            human-review support
          </p>

        </div>

        <Activity size={18} />

      </div>


      <div className="pipeline">

        {steps.map(function (
          step,
          index
        ) {

          const Icon = step.icon;

          return (
            <React.Fragment
              key={step.title}
            >

              <div className="pipeline-step">

                <Icon size={18} />

                <strong>
                  {step.title}
                </strong>

                <span>
                  {step.text}
                </span>

              </div>


              {index <
                steps.length - 1 && (
                <div className="pipeline-arrow">
                  →
                </div>
              )}

            </React.Fragment>
          );

        })}

      </div>

    </div>
  );
}


/* =========================================================
   COMMAND CENTER
   ========================================================= */

function CommandCenter({
  scenarios,
  selectedScenario,
  setSelectedId,
  monitoredId,
  onToggleMonitoring
}) {

  const spatialCount =
    scenarios.filter(function (s) {
      return s.spatialEvidenceAvailable;
    }).length;


  return (
    <>

      <div className="page-header">

        <div>

          <span className="eyebrow">
            QUAKESHIELD / HISTORICAL SCENARIO REVIEW
          </span>

          <h1>
            Command Center
          </h1>

          <p>
            Screening co-seismic secondary-hazard
            indicators using historical earthquake
            scenarios, model outputs, spatial evidence,
            and infrastructure context.
          </p>

        </div>


        <div className="status-pill">

          <span />

          MODELS OPERATIONAL

        </div>

      </div>


      <div className="stats">

        <div className="stat-card">

          <span className="stat-label">
            TOTAL SCENARIOS
          </span>

          <span className="stat-value">
            {scenarios.length}
          </span>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            SPATIAL EVIDENCE CASES
          </span>

          <span className="stat-value">
            {spatialCount}
          </span>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            MODEL INDICATORS
          </span>

          <span className="stat-value">
            2
          </span>

        </div>

      </div>


      <div className="command-grid">

        <ScenarioMap
          scenarios={scenarios}
          selectedScenario={selectedScenario}
          onSelect={setSelectedId}
        />


        <ScenarioDetails
          scenario={selectedScenario}
          monitoredId={monitoredId}
          onToggleMonitoring={
            onToggleMonitoring
          }
        />

      </div>


      <Pipeline />

    </>
  );
}


/* =========================================================
   MONITORING PAGE
   ========================================================= */

function MonitoringPage({
  scenarios,
  monitoredId,
  setSelectedId,
  onToggleMonitoring
}) {

  const monitoredScenario =
    scenarios.find(function (scenario) {
      return scenario.id === monitoredId;
    });


  if (!monitoredScenario) {

    return (
      <>

        <div className="page-header">

          <div>

            <span className="eyebrow">
              MONITORING / HUMAN REVIEW
            </span>

            <h1>
              Monitoring & Review
            </h1>

            <p>
              Select a scenario to keep visible
              during prototype review.
            </p>

          </div>

        </div>


        <div className="monitor-list">

          {scenarios.map(function (
            scenario
          ) {

            return (
              <div
                className="monitor-card"
                key={scenario.id}
              >

                <div className="monitor-card-header">

                  <div>

                    <h2>
                      {scenario.name}
                    </h2>

                    <p>
                      {scenario.country}
                    </p>

                  </div>

                </div>


                <div className="details-grid">

                  <div className="detail-item">

                    <span>
                      P1 SCORE
                    </span>

                    <strong>
                      {score(scenario.p1)}
                    </strong>

                  </div>


                  <div className="detail-item">

                    <span>
                      P2 SCORE
                    </span>

                    <strong>
                      {score(scenario.p2)}
                    </strong>

                  </div>


                  <div className="detail-item">

                    <span>
                      SPATIAL EVIDENCE
                    </span>

                    <strong>
                      {scenario.spatialEvidenceAvailable
                        ? "AVAILABLE"
                        : "NONE"}
                    </strong>

                  </div>

                </div>


                <div className="monitor-actions">

                  <button
                    className="command-secondary"
                    onClick={function () {
                      setSelectedId(
                        scenario.id
                      );
                    }}
                  >
                    View Scenario
                  </button>


                  <button
                    className="command-primary"
                    onClick={function () {
                      onToggleMonitoring(
                        scenario.id
                      );
                    }}
                  >
                    Monitor for Review
                  </button>

                </div>

              </div>
            );

          })}

        </div>

      </>
    );
  }


  return (
    <>

      <div className="page-header">

        <div>

          <span className="eyebrow">
            PROTOTYPE REVIEW STATE
          </span>

          <h1>
            Monitoring & Review
          </h1>

          <p>
            Review monitoring is active for{" "}
            <strong>
              {monitoredScenario.name}
            </strong>
            .
          </p>

        </div>


        <div className="status-pill">

          <span />

          REVIEW MONITORING

        </div>

      </div>


      <div className="monitor-list">

        <div className="monitor-card">

          <div className="monitor-card-header">

            <div>

              <h2>
                {monitoredScenario.name}
              </h2>

              <p>
                {monitoredScenario.location}
              </p>

            </div>

          </div>


          <div className="details-grid">

            <div className="detail-item">

              <span>
                P1 SCORE
              </span>

              <strong>
                {score(
                  monitoredScenario.p1
                )}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                P2 MODEL SCORE
              </span>

              <strong>
                {score(
                  monitoredScenario.p2
                )}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                SPATIAL EVIDENCE
              </span>

              <strong>
                {monitoredScenario
                  .spatialEvidenceAvailable
                  ? "AVAILABLE"
                  : "NONE"}
              </strong>

            </div>


            <div className="detail-item">

              <span>
                INFRASTRUCTURE
              </span>

              <strong>
                {infrastructureLabel(
                  monitoredScenario.infrastructureCount
                )}
              </strong>

            </div>

          </div>


          <p className="method-note">

            This monitoring state is only a
            prototype review feature. It does not
            represent a real-time emergency alert
            or operational warning system.

          </p>


          <div className="monitor-actions">

            <button
              className="command-secondary"
              onClick={function () {
                setSelectedId(
                  monitoredScenario.id
                );
              }}
            >
              View Scenario
            </button>


            <button
              className="command-primary"
              onClick={function () {
                onToggleMonitoring(
                  monitoredScenario.id
                );
              }}
            >

              <EyeOff
                size={15}
                style={{
                  marginRight: "7px"
                }}
              />

              Stop Review Monitoring

            </button>

          </div>

        </div>

      </div>

    </>
  );
}


/* =========================================================
   SCENARIOS PAGE
   ========================================================= */

function ScenariosPage({
  scenarios,
  setSelectedId
}) {

  return (
    <>

      <div className="page-header">

        <div>

          <span className="eyebrow">
            ANALYSIS / SCENARIO REGISTER
          </span>

          <h1>
            Hazard Scenarios
          </h1>

          <p>
            Historical earthquake scenarios with
            separate ground-failure and liquefaction
            model indicators.
          </p>

        </div>


        <div className="status-pill">

          <span />

          {scenarios.length} SCENARIOS

        </div>

      </div>


      <div className="scenario-grid">

        {scenarios.map(function (
          scenario
        ) {

          return (
            <div
              className="scenario-card"
              key={scenario.id}
            >

              <span
                className="eyebrow"
                style={{
                  color:
                    scenario.spatialEvidenceAvailable
                      ? "#2563eb"
                      : "#64748b"
                }}
              >
                {scenario.spatialEvidenceAvailable
                  ? "SPATIAL EVIDENCE AVAILABLE"
                  : "NO VERIFIED SPATIAL EVIDENCE"}
              </span>


              <h3>
                {scenario.name}
              </h3>


              <p>
                {scenario.country}
              </p>


              <p>
                Magnitude:{" "}
                {scenario.magnitude}
              </p>


              <div className="details-grid">

                <div className="detail-item">

                  <span>
                    P1
                  </span>

                  <strong>
                    {score(scenario.p1)}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    P2
                  </span>

                  <strong>
                    {score(scenario.p2)}
                  </strong>

                </div>

              </div>


              <p className="method-note">

                {scenario.reviewContext}

              </p>


              <div className="command-actions">

                <button
                  className="command-secondary"
                  onClick={function () {
                    setSelectedId(
                      scenario.id
                    );
                  }}
                >
                  View Scenario
                </button>

              </div>

            </div>
          );

        })}

      </div>

    </>
  );
}


/* =========================================================
   SCENARIO INDICATORS PAGE
   ========================================================= */

function RiskPage({
  scenarios
}) {

  const averageP1 =
    scenarios.length
      ? scenarios.reduce(
          function (sum, scenario) {
            return sum + scenario.p1;
          },
          0
        ) / scenarios.length
      : 0;


  const averageP2 =
    scenarios.length
      ? scenarios.reduce(
          function (sum, scenario) {
            return sum + scenario.p2;
          },
          0
        ) / scenarios.length
      : 0;


  const spatialCases =
    scenarios.filter(function (scenario) {
      return scenario.spatialEvidenceAvailable;
    }).length;


  return (
    <>

      <div className="page-header">

        <div>

          <span className="eyebrow">
            ANALYSIS / SCENARIO INDICATORS
          </span>

          <h1>
            Scenario Indicators
          </h1>

          <p>
            Transparent interpretation of separate
            model indicators and verified spatial
            evidence.
          </p>

        </div>

      </div>


      <div className="risk-method-grid">

        <div className="risk-method-card">

          <div className="method-icon">
            <TrendingUp size={20} />
          </div>

          <h3>
            P1 — Ground-Failure Model
          </h3>

          <p>
            The current P1 formulation uses slope
            as the selected predictor in a Logistic
            Regression model. Its output is treated
            as a relative ground-failure model score,
            not a calibrated probability.
          </p>

        </div>


        <div className="risk-method-card">

          <div className="method-icon">
            <Waves size={20} />
          </div>

          <h3>
            P2 — Liquefaction Model
          </h3>

          <p>
            The existing liquefaction classifier
            provides the P2 liquefaction model score.
            The value is an uncalibrated model
            indicator and should not be interpreted
            as a probability of liquefaction.
          </p>

        </div>


        <div className="risk-method-card">

          <div className="method-icon">
            <MapPin size={20} />
          </div>

          <h3>
            Spatial Evidence
          </h3>

          <p>
            Verified historical cases, mapped NGL
            anchors, and direct USGS ShakeMap PGA
            values are retained as separate review
            evidence where available.
          </p>

        </div>


        <div className="risk-method-card">

          <div className="method-icon">
            <Shield size={20} />
          </div>

          <h3>
            Human Review
          </h3>

          <p>
            QuakeShield presents model outputs and
            supporting context to assist human review.
            The current prototype does not automatically
            issue public warnings.
          </p>

        </div>

      </div>


      <div className="assessment-card">

        <div className="assessment-title">

          <Activity size={15} />

          CURRENT DATASET SUMMARY

        </div>


        <div className="details-grid">

          <div className="detail-item">

            <span>
              SCENARIOS
            </span>

            <strong>
              {scenarios.length}
            </strong>

          </div>


          <div className="detail-item">

            <span>
              AVERAGE P1 SCORE
            </span>

            <strong>
              {score(averageP1)}
            </strong>

          </div>


          <div className="detail-item">

            <span>
              AVERAGE P2 MODEL SCORE
            </span>

            <strong>
              {score(averageP2)}
            </strong>

          </div>


          <div className="detail-item">

            <span>
              SPATIAL EVIDENCE CASES
            </span>

            <strong>
              {spatialCases}
            </strong>

          </div>

        </div>

      </div>


      <div className="communication-flow">

        <div className="communication-step">

          <span className="communication-number">
            STEP 01
          </span>

          <strong>
            Hazard Evidence
          </strong>

          <p>
            Historical earthquake information,
            terrain information, and prepared
            geotechnical data establish the
            scenario context.
          </p>

        </div>


        <div className="communication-step">

          <span className="communication-number">
            STEP 02
          </span>

          <strong>
            Separate Model Indicators
          </strong>

          <p>
            P1 and P2 produce independent model
            scores for ground failure and
            liquefaction.
          </p>

        </div>


        <div className="communication-step">

          <span className="communication-number">
            STEP 03
          </span>

          <strong>
            Spatial Context
          </strong>

          <p>
            Where verified evidence exists, historical
            liquefaction cases, mapped anchors and
            ShakeMap observations are shown separately.
          </p>

        </div>


        <div className="communication-step">

          <span className="communication-number">
            STEP 04
          </span>

          <strong>
            Human Review
          </strong>

          <p>
            Infrastructure and model evidence are
            presented as decision-support context
            for further human assessment.
          </p>

        </div>

      </div>


      <div className="assessment-card">

        <div className="assessment-title">

          <Shield size={15} />

          IMPORTANT INTERPRETATION NOTE

        </div>

        <p className="method-note">

          QuakeShield is currently a historical
          co-seismic secondary-hazard screening
          prototype. It is not a real-time earthquake
          detection system, calibrated probability
          engine, damage predictor, or automatic
          public alert system.

        </p>

      </div>

    </>
  );
}


/* =========================================================
   INFRASTRUCTURE PAGE
   ========================================================= */

function InfrastructurePage({
  scenarios
}) {

  return (
    <>

      <div className="page-header">

        <div>

          <span className="eyebrow">
            CONTEXT / MAPPED INFRASTRUCTURE
          </span>

          <h1>
            Infrastructure
          </h1>

          <p>
            Geographic infrastructure context around
            representative scenario locations.
          </p>

        </div>

      </div>


      <div className="scenario-grid">

        {scenarios.map(function (
          scenario
        ) {

          return (
            <div
              className="scenario-card"
              key={scenario.id}
            >

              <h3>
                {scenario.name}
              </h3>

              <p>
                {scenario.country}
              </p>


              <div className="infrastructure-grid">

                <div className="infra-card">

                  <span>
                    HOSPITAL
                  </span>

                  <strong>
                    {scenario.hospitalCount > 0
                      ? `${scenario.hospitalCount} mapped`
                      : "No mapped data"}
                  </strong>

                </div>


                <div className="infra-card">

                  <span>
                    SCHOOL
                  </span>

                  <strong>
                    {scenario.schoolCount > 0
                      ? `${scenario.schoolCount} mapped`
                      : "No mapped data"}
                  </strong>

                </div>


                <div className="infra-card">

                  <span>
                    BRIDGE
                  </span>

                  <strong>
                    {scenario.bridgeCount > 0
                      ? `${scenario.bridgeCount} mapped`
                      : "No mapped data"}
                  </strong>

                </div>


                <div className="infra-card">

                  <span>
                    ROAD
                  </span>

                  <strong>
                    {scenario.roadCount > 0
                      ? `${scenario.roadCount} mapped`
                      : "No mapped data"}
                  </strong>

                </div>

              </div>


              <p className="method-note">

                {infrastructureLabel(
                  scenario.infrastructureCount
                )}

                . The infrastructure query is centered
                on the representative scenario dataset
                cell, not necessarily a verified earthquake
                epicenter.

              </p>

            </div>
          );

        })}

      </div>


      <div className="assessment-card">

        <div className="assessment-title">

          <Building2 size={15} />

          INFRASTRUCTURE INTERPRETATION

        </div>

        <p className="method-note">

          Infrastructure results provide mapped
          geographic context only. They do not
          establish exposure, vulnerability, damage,
          impact, or safety status. Zero returned
          features mean that no mapped features were
          returned by the current query.

        </p>

      </div>

    </>
  );
}


/* =========================================================
   APP
   ========================================================= */

export default function App() {

  const [page, setPage] =
    useState("command");

  const [selectedId, setSelectedId] =
    useState(
      scenarios.length
        ? scenarios[0].id
        : null
    );

  const [monitoredId, setMonitoredId] =
    useState(null);


  const selectedScenario =
    useMemo(
      function () {
        return scenarios.find(
          function (scenario) {
            return scenario.id === selectedId;
          }
        );
      },
      [selectedId]
    );


  function toggleMonitoring(id) {

    setMonitoredId(
      function (current) {
        return current === id
          ? null
          : id;
      }
    );

  }


  function renderPage() {

    if (page === "command") {

      return (
        <CommandCenter
          scenarios={scenarios}
          selectedScenario={selectedScenario}
          setSelectedId={setSelectedId}
          monitoredId={monitoredId}
          onToggleMonitoring={
            toggleMonitoring
          }
        />
      );

    }


    if (page === "monitoring") {

      return (
        <MonitoringPage
          scenarios={scenarios}
          monitoredId={monitoredId}
          setSelectedId={setSelectedId}
          onToggleMonitoring={
            toggleMonitoring
          }
        />
      );

    }


    if (page === "scenarios") {

      return (
        <ScenariosPage
          scenarios={scenarios}
          setSelectedId={setSelectedId}
        />
      );

    }


    if (page === "risk") {

      return (
        <RiskPage
          scenarios={scenarios}
        />
      );

    }


    if (page === "infrastructure") {

      return (
        <InfrastructurePage
          scenarios={scenarios}
        />
      );

    }


    return null;
  }


  return (
    <div className="app-shell">

      {/* =====================================================
         SIDEBAR
         ===================================================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            QS
          </div>

          <div>

            <strong>
              QUAKESHIELD
            </strong>

            <span>
              HAZARD INTELLIGENCE
            </span>

          </div>

        </div>


        <nav className="sidebar-nav">

          {navItems.map(function (
            group
          ) {

            return (
              <div
                className="nav-group"
                key={group.group}
              >

                <div className="nav-group-title">
                  {group.group}
                </div>


                {group.items.map(
                  function (item) {

                    const Icon =
                      item.icon;

                    const active =
                      page === item.id;

                    return (
                      <button
                        key={item.id}
                        className={
                          active
                            ? "nav-item active"
                            : "nav-item"
                        }
                        onClick={function () {
                          setPage(item.id);
                        }}
                      >

                        <Icon size={17} />

                        <span>
                          {item.label}
                        </span>

                      </button>
                    );

                  }
                )}

              </div>
            );

          })}

        </nav>


        <div className="sidebar-footer">

          <div className="system-status">

            <span />

            SYSTEM STATUS

          </div>

          <strong>
            MODELS OPERATIONAL
          </strong>

          <small>
            Historical scenario prototype
          </small>

        </div>

      </aside>


      {/* =====================================================
         MAIN CONTENT
         ===================================================== */}

      <main className="main-content">

        {renderPage()}

      </main>

    </div>
  );
}