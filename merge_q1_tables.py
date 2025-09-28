import pandas as pd

acc = pd.read_csv("results/q1_summary.csv")  # condition, n, accuracy, ci_lo, ci_hi
flu = pd.read_csv("results/q1_fluency_summary.csv")  # condition, avg_fluency, n_rated

# Optional: pretty labels for the report (keeps originals too)
pretty = {
    "L1EN": "English (L1)",
    "L2MR": "Marathi (L2)",
    "L3HINGLISH": "Hinglish (L3)",
    "CSMIXED": "Code-Switched"
}

acc["cond_pretty"] = acc["condition"].map(pretty).fillna(acc["condition"])
flu["cond_pretty"] = flu["condition"].map(pretty).fillna(flu["condition"])

merged = pd.merge(
    acc,
    flu[["condition", "avg_fluency", "n_rated"]],
    on="condition",
    how="left"
)

# Reorder and round for readability
merged["cond_pretty"] = merged["condition"].map(pretty).fillna(merged["condition"])
cols = ["cond_pretty","condition","n","accuracy","ci_lo","ci_hi","avg_fluency","n_rated"]
merged = merged[cols]
for c in ["accuracy","ci_lo","ci_hi","avg_fluency"]:
    merged[c] = merged[c].astype(float).round(2)

merged = merged.sort_values("cond_pretty")
merged.to_csv("results/q1_combined.csv", index=False)
print("Wrote results/q1_combined.csv")
print(merged)
