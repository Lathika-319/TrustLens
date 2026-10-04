
export const scenarioData = [
  {
    location: "Tohoku-Oki, Japan",
    date: "2011-03-11",
    lat: 38.915,
    lon: 140.735,
    magnitude: 9.1,
    depthKm: 29,

    groundFailure: 0.410811,
    liquefaction: 0.734410,

    spatialEvidence: true,
    spatialScenario: "Tohoku-Oki",
    anchorCount: 5,
    historicalRecords: 18,
    meanShakeMapPGA: 0.371407,
    historicalLRate: 0.828571,

    infrastructureCount: 2,
    nearestInfrastructureKm: 0.281481,
    hospitalCount: 0,
    schoolCount: 0,
    bridgeCount: 1,
    roadCount: 1,

    reviewContext:
      "SPATIAL EVIDENCE AVAILABLE FOR REVIEW",

    explanation:
      "Tohoku-Oki, Japan: P1 ground-failure model score is 0.411. P2 liquefaction model score is 0.734. Verified spatial evidence is available for review, including 5 mapped anchors and 18 historical records. Mean current ShakeMap PGA across the anchors is 0.371 g. Historical liquefaction outcome rate across the matched evidence is 0.829. Mapped infrastructure query returned 2 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "1 km S of Belanting, Indonesia",
    date: "2018-08-05",
    lat: -8.287,
    lon: 116.461,
    magnitude: 6.9,
    depthKm: 31,

    groundFailure: 0.374147,
    liquefaction: 0.596000,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 4,
    nearestInfrastructureKm: 0.754495,
    hospitalCount: 1,
    schoolCount: 1,
    bridgeCount: 1,
    roadCount: 1,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "1 km S of Belanting, Indonesia: P1 ground-failure model score is 0.374. P2 liquefaction model score is 0.596. No verified spatial evidence is available for this scenario in the current prototype. Mapped infrastructure query returned 4 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "70km N of Palu, Indonesia",
    date: "2018-09-28",
    lat: -0.178,
    lon: 119.840,
    magnitude: 7.5,
    depthKm: 10,

    groundFailure: 0.501359,
    liquefaction: 0.443944,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 4,
    nearestInfrastructureKm: 2.411023,
    hospitalCount: 1,
    schoolCount: 1,
    bridgeCount: 1,
    roadCount: 1,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "70km N of Palu, Indonesia: P1 ground-failure model score is 0.501. P2 liquefaction model score is 0.444. No verified spatial evidence is available for this scenario in the current prototype. Mapped infrastructure query returned 4 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "32 km SW of Tari, Papua New Guinea",
    date: "2018-02-25",
    lat: -6.077,
    lon: 142.776,
    magnitude: 7.5,
    depthKm: 35,

    groundFailure: 0.486531,
    liquefaction: 0.443944,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 0,
    nearestInfrastructureKm: null,
    hospitalCount: 0,
    schoolCount: 0,
    bridgeCount: 0,
    roadCount: 0,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "32 km SW of Tari, Papua New Guinea: P1 ground-failure model score is 0.487. P2 liquefaction model score is 0.444. No verified spatial evidence is available for this scenario in the current prototype. No mapped infrastructure features were returned by the query. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "9 km NW of Mesetas, Colombia",
    date: "2023-08-17",
    lat: 3.744,
    lon: -74.044,
    magnitude: 6.3,
    depthKm: 10,

    groundFailure: 0.413763,
    liquefaction: 0.665242,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 2,
    nearestInfrastructureKm: 7.185311,
    hospitalCount: 0,
    schoolCount: 1,
    bridgeCount: 1,
    roadCount: 0,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "9 km NW of Mesetas, Colombia: P1 ground-failure model score is 0.414. P2 liquefaction model score is 0.665. No verified spatial evidence is available for this scenario in the current prototype. Mapped infrastructure query returned 2 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "M 6.4 - 13 km SSE of Maria Antonia, Puerto Rico",
    date: "2020-01-07",
    lat: 18.011,
    lon: -66.809,
    magnitude: 6.4,
    depthKm: 9,

    groundFailure: 0.399006,
    liquefaction: 0.746539,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 0,
    nearestInfrastructureKm: null,
    hospitalCount: 0,
    schoolCount: 0,
    bridgeCount: 0,
    roadCount: 0,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "M 6.4 - 13 km SSE of Maria Antonia, Puerto Rico: P1 ground-failure model score is 0.399. P2 liquefaction model score is 0.747. No verified spatial evidence is available for this scenario in the current prototype. No mapped infrastructure features were returned by the query. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "Kobe, Japan",
    date: "1995-01-17",
    lat: 34.595,
    lon: 135.120,
    magnitude: 6.9,
    depthKm: 17,

    groundFailure: 0.576772,
    liquefaction: 0.596000,

    spatialEvidence: true,
    spatialScenario: "Kobe",
    anchorCount: 3,
    historicalRecords: 55,
    meanShakeMapPGA: 0.708165,
    historicalLRate: 0.666667,

    infrastructureCount: 4,
    nearestInfrastructureKm: 0.114987,
    hospitalCount: 1,
    schoolCount: 1,
    bridgeCount: 1,
    roadCount: 1,

    reviewContext:
      "SPATIAL EVIDENCE AVAILABLE FOR REVIEW",

    explanation:
      "Kobe, Japan: P1 ground-failure model score is 0.577. P2 liquefaction model score is 0.596. Verified spatial evidence is available for review, including 3 mapped anchors and 55 historical records. Mean current ShakeMap PGA across the anchors is 0.708 g. Historical liquefaction outcome rate across the matched evidence is 0.667. Mapped infrastructure query returned 4 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "Niigata-Chuetsu, Japan",
    date: "2004-10-23",
    lat: 37.289,
    lon: 138.870,
    magnitude: 6.6,
    depthKm: 13,

    groundFailure: 0.485846,
    liquefaction: 0.556208,

    spatialEvidence: true,
    spatialScenario: "Niigata-Chuetsu",
    anchorCount: 3,
    historicalRecords: 3,
    meanShakeMapPGA: 0.100947,
    historicalLRate: 0.333333,

    infrastructureCount: 0,
    nearestInfrastructureKm: null,
    hospitalCount: 0,
    schoolCount: 0,
    bridgeCount: 0,
    roadCount: 0,

    reviewContext:
      "SPATIAL EVIDENCE AVAILABLE FOR REVIEW",

    explanation:
      "Niigata-Chuetsu, Japan: P1 ground-failure model score is 0.486. P2 liquefaction model score is 0.556. Verified spatial evidence is available for review, including 3 mapped anchors and 3 historical records. Mean current ShakeMap PGA across the anchors is 0.101 g. Historical liquefaction outcome rate across the matched evidence is 0.333. No mapped infrastructure features were returned by the query. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  },

  {
    location: "Kashmir, Pakistan",
    date: "2005-10-08",
    lat: 34.539,
    lon: 73.588,
    magnitude: 7.6,
    depthKm: 26,

    groundFailure: 0.692160,
    liquefaction: 0.483211,

    spatialEvidence: false,
    spatialScenario: null,
    anchorCount: null,
    historicalRecords: null,
    meanShakeMapPGA: null,
    historicalLRate: null,

    infrastructureCount: 4,
    nearestInfrastructureKm: 1.374332,
    hospitalCount: 1,
    schoolCount: 1,
    bridgeCount: 1,
    roadCount: 1,

    reviewContext:
      "NO VERIFIED SPATIAL EVIDENCE IN CURRENT PROTOTYPE",

    explanation:
      "Kashmir, Pakistan: P1 ground-failure model score is 0.692. P2 liquefaction model score is 0.483. No verified spatial evidence is available for this scenario in the current prototype. Mapped infrastructure query returned 4 features. These outputs are screening indicators and review context, not calibrated probabilities, damage estimates, or automatic alerts."
  }
];
