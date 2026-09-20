import pandas as pd

# Load fusion inputs
df = pd.read_csv("risk_fusion_inputs.csv")

# --------------------------------------------------
# Risk Fusion
# --------------------------------------------------
# P1 = ground-failure probability
# P2 = liquefaction probability
#
# Multiplicative score represents joint cascading
# hazard risk at the scenario level.
# --------------------------------------------------

df["final_risk_score"] = (
    df["P1_ground_failure_probability"]
    * df["mean_P2_liquefaction_probability"]
)

# --------------------------------------------------
# Risk categories
# --------------------------------------------------

def classify_risk(score):
    if score >= 0.60:
        return "HIGH"
    elif score >= 0.30:
        return "MEDIUM"
    else:
        return "LOW"

df["risk_level"] = df["final_risk_score"].apply(
    classify_risk
)

# Sort highest risk first
df = df.sort_values(
    "final_risk_score",
    ascending=False
)

# Save final risk output
output_file = "final_risk_scores.csv"

df.to_csv(
    output_file,
    index=False
)

print("=" * 70)
print("QUAKESHIELD RISK FUSION COMPLETED")
print("=" * 70)

print("\nFinal risk scores:")
print(
    df[
        [
            "earthquake_name",
            "P1_ground_failure_probability",
            "mean_P2_liquefaction_probability",
            "final_risk_score",
            "risk_level"
        ]
    ].to_string(index=False)
)

print("\nRisk-level counts:")
print(df["risk_level"].value_counts())

print("\nSaved:")
print(output_file)
