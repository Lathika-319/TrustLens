\# QuakeShield Multi-Hazard Architecture



\## 1. Purpose



QuakeShield is a modular prototype for screening co-seismic secondary hazards using historical earthquake scenarios, hazard-specific model indicators, verified spatial evidence, and geographic context.



The system is designed for human review.



It does not currently provide:



\* calibrated hazard probabilities

\* automatic risk classification

\* damage prediction

\* exposure or vulnerability assessment

\* automatic public warnings

\* real-time emergency response



\---



\## 2. Core Architecture



Each secondary hazard is represented as an independent hazard module.



```text

&#x20;                   Earthquake Scenario

&#x20;                          |

&#x20;         +----------------+----------------+

&#x20;         |                |                |

&#x20;         v                v                v

&#x20;    Hazard Module    Hazard Module    Evidence Layer

&#x20;         |                |                |

&#x20;         v                v                v

&#x20;   Ground Failure    Liquefaction     Historical Cases

&#x20;      P1 Score          P2 Score       ShakeMap PGA

&#x20;         |                |                |

&#x20;         +----------------+----------------+

&#x20;                          |

&#x20;                          v

&#x20;                   Review Context

&#x20;                          |

&#x20;                          v

&#x20;                    Human Review

```



\---



\## 3. Hazard Module Contract



Each hazard module should provide:



\### Required



\* hazard identifier

\* hazard name

\* model identifier

\* model score

\* feature inputs

\* model version

\* dataset version

\* evaluation information

\* limitations



\### Optional



\* spatial evidence

\* historical evidence

\* supporting measurements

\* confidence metadata

\* explanation text



A module must not automatically convert its score into a universal probability unless calibration has been explicitly validated.



\---



\## 4. Current Modules



\### P1 — Ground Failure



Model:



Slope + PGA logistic regression.



Inputs:



\* slope\_degrees

\* PGA\_g



Output:



`P1\_ground\_failure\_score`



Interpretation:



Ground-failure model indicator.



Current validation:



\* LOEO mean AUC: 0.7177

\* 9 earthquake scenarios

\* within-earthquake permutation diagnostic

\* empirical one-sided p ≈ 0.0099 for the permutation diagnostic



Limitations:



\* score is not a calibrated probability

\* background cells are not confirmed unaffected

\* prepared dataset contains sampling structure

\* results do not establish universal future-event performance

\* PGA association should not be interpreted as causal proof



\---



\### P2 — Liquefaction



Model:



Gradient Boosting Classifier.



Inputs include:



\* effective stress ratio

\* `(N1)60`

\* `qt1N`

\* `Ic`

\* `VS1`

\* fines content

\* depth

\* earthquake magnitude

\* PGA

\* missingness indicators



Output:



`P2\_liquefaction\_model\_score`



Interpretation:



Liquefaction model indicator.



Limitations:



\* score is not calibrated

\* current scenario mapping uses nearest available magnitude

\* P2 training sites are not co-located with P1 grid cells

\* current implementation is not an event-specific spatial liquefaction map

\* spatial evidence is therefore kept separately



\---



\## 5. Spatial Evidence Layer



Spatial evidence is not another hazard score.



It provides supporting historical and geographic context.



Current evidence includes:



\* verified historical liquefaction records

\* mapped NGL anchors

\* USGS ShakeMap PGA at verified anchors

\* historical liquefaction outcomes

\* historical PGA ranges



Current verified scenarios:



\* Tohoku-Oki

\* Kobe

\* Niigata-Chuetsu



Spatial evidence should be displayed separately from P1 and P2 indicators.



\---



\## 6. Infrastructure Context



Infrastructure is contextual geographic information.



Current implementation:



\* hospitals

\* schools

\* bridges

\* roads



The current query uses a representative scenario location.



Therefore the output must be described as:



> Mapped infrastructure proximity context around the representative scenario location.



It must not be interpreted as:



\* exposure

\* vulnerability

\* damage

\* affected population

\* safety assessment



Zero returned features means no features were returned by the current query. It does not prove that infrastructure is absent.



\---



\## 7. Multi-Hazard Principle



QuakeShield must not combine independent hazard indicators through an unvalidated arithmetic formula.



Examples that must NOT be treated as validated hazard fusion:



```text

P1 × P2

```



```text

(P1 + P2) / 2

```



```text

weighted P1 + weighted P2

```



```text

maximum(P1, P2)

```



These operations can be explored experimentally, but they must not be presented as calibrated risk or probability without appropriate validation.



\---



\## 8. Review-Oriented Output



The primary output should preserve hazard-specific information.



Example:



```text

Scenario: Kobe, Japan



Ground Failure

&#x20;   P1 score: 0.577



Liquefaction

&#x20;   P2 score: 0.596



Spatial Evidence

&#x20;   Anchors: 3

&#x20;   Historical records: 55

&#x20;   Mean ShakeMap PGA: 0.708 g

&#x20;   Historical liquefaction rate: 66.7%



Infrastructure Context

&#x20;   Mapped features: 4



Review

&#x20;   Human interpretation required

```



The system should allow a reviewer to understand:



1\. Which hazard is being indicated.

2\. Which model produced the indicator.

3\. What evidence supports the scenario.

4\. What geographic context is available.

5\. What limitations remain.



\---



\## 9. Future Hazard Modules



Future modules may include:



\* landslide susceptibility

\* liquefaction

\* lateral spreading

\* tsunami

\* rockfall

\* earthquake-triggered landslide

\* other scientifically justified secondary hazards



A new module should not require rewriting the entire pipeline.



Instead:



```text

Earthquake Scenario

&#x20;      |

&#x20;      +---- P1 Ground Failure

&#x20;      |

&#x20;      +---- P2 Liquefaction

&#x20;      |

&#x20;      +---- P3 Future Hazard

&#x20;      |

&#x20;      +---- P4 Future Hazard

&#x20;      |

&#x20;      +---- Spatial Evidence

&#x20;      |

&#x20;      +---- Infrastructure Context

&#x20;      |

&#x20;      v

Review Context

```



\---



\## 10. Design Rule



The system should answer:



> "What does each hazard-specific model and evidence layer indicate, and why should a reviewer look at it?"



It should not answer:



> "What is the single numerical risk of this earthquake?"



unless a future scientifically validated fusion framework is developed.



\---



\## 11. Current Status



\### Implemented



\* P1 Ground Failure

\* P2 Liquefaction

\* Historical spatial evidence

\* ShakeMap evidence

\* Infrastructure context

\* Human-review dashboard



\### Not yet implemented



\* Additional hazard module

\* Validated multi-hazard fusion

\* Dynamic post-earthquake intelligence

\* Authority approval workflow

\* Public alerting



\---



\## 12. Versioning Principle



Every hazard module should retain:



\* model file

\* training dataset

\* feature list

\* evaluation result

\* validation script

\* model limitations



This allows individual modules to be improved without silently changing the interpretation of other hazards.


## P4 Lateral Spreading — Research Evaluation

Lateral spreading was investigated as an additional secondary-hazard module using
Next Generation Liquefaction (NGL) field observations.

The dataset was constructed at the field-observation level to avoid assigning
multiple contradictory manifestation labels to the same observation. Mixed-label
observations were excluded.

Final research dataset:

- 299 clean field observations
- 36 earthquake event groups
- 37 positive observations
- 262 negative observations
- PGA coverage: 100%
- PGV coverage: 99%
- Arias Intensity coverage: 99%
- No duplicate field observations
- No missing event or site linkage
- No displacement variables used as predictors
- No manifestation outcome fields used as predictors

Candidate predictors:

- PGA_g
- PGV_mps
- Arias_Intensity

Validation used Leave-One-Earthquake-Out (LOEO) evaluation.

Observed LOEO ROC-AUC:

    0.5362

A within-earthquake permutation diagnostic was then performed using 100
permutations.

Permutation results:

- Null mean: 0.5377
- Null standard deviation: 0.0676
- Null 95th percentile: 0.6311
- Permutations greater than or equal to observed: 57/100
- Empirical p-value: 0.5743

### Decision

The observed P4 performance was not distinguishable from the
within-earthquake permutation null.

Therefore:

- P4 is NOT promoted to production.
- P4 is NOT connected to the active hazard registry.
- P4 is NOT connected to the production pipeline.
- P4 is NOT displayed as an operational hazard indicator.
- The research dataset, validation results, and candidate model are retained
  for reproducibility and future investigation.

This is treated as a model rejection based on insufficient evidence rather than
as evidence that lateral spreading is unimportant.
