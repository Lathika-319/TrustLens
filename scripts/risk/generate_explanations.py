import pandas as pd

# Load final risk scores
df = pd.read_csv("final_risk_scores.csv")


def generate_explanation(row):
    p1 = row["P1_ground_failure_probability"]
    p2 = row["mean_P2_liquefaction_probability"]
    risk = row["final_risk_score"]

    reasons = []

    if p1 >= 0.60:
        reasons.append("high ground-failure probability")
    elif p1 >= 0.50:
        reasons.append("moderate ground-failure probability")
    else:
        reasons.append("lower ground-failure probability")

    if p2 >= 0.70:
        reasons.append("high liquefaction probability")
    elif p2 >= 0.50:
        reasons.append("moderate liquefaction probability")
    else:
        reasons.append("lower liquefaction probability")

    if risk >= 0.60:
        risk_text = "The combined cascading-hazard score is high."
    elif risk >= 0.30:
        risk_text = "The combined cascading-hazard score is medium."
    else:
        risk_text = "The combined cascading-hazard score is low."

    return (
        "Risk is influenced by "
        + " and ".join(reasons)
        + ". "
        + risk_text
    )


# Generate explanation for every earthquake
df["risk_explanation"] = df.apply(
    generate_explanation,
    axis=1
)

# Create explanation-ready output
explanation_data = df[
    [
        "earthquake_id",
        "earthquake_name",
        "latitude",
        "longitude",
        "P1_ground_failure_probability",
        "mean_P2_liquefaction_probability",
        "final_risk_score",
        "risk_level",
        "risk_explanation"
    ]
].copy()

# Save
output_file = "quakeshield_explanations.csv"

explanation_data.to_csv(
    output_file,
    index=False
)

print("=" * 70)
print("QUAKESHIELD EXPLAINABILITY COMPLETED")
print("=" * 70)

print("\nGenerated explanations:", len(explanation_data))

print("\nSample explanations:")

for _, row in explanation_data.head(5).iterrows():
    print("\nLocation:", row["earthquake_name"])
    print("Risk:", row["risk_level"])
    print("Explanation:", row["risk_explanation"])

print("\nSaved:")
print(output_file)
