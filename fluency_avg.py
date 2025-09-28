import pandas as pd

# Load CSV
df = pd.read_csv("results/q1_results.csv")

# Strip column names of hidden spaces
df.columns = df.columns.str.strip()

# Always take the last column as fluency (to handle trailing commas issue)
fluency_col = df.columns[-1]

# Force clean fluency values: strip spaces, drop quotes, convert to numeric
df['fluency'] = df[fluency_col].astype(str).str.strip()
df['fluency'] = pd.to_numeric(df['fluency'], errors='coerce')

# Keep only rows with valid fluency numbers
df = df.dropna(subset=['fluency'])

# Group by condition: average + count
summary = df.groupby("condition").agg(
    avg_fluency=("fluency", "mean"),
    n_rated=("fluency", "count")
).reset_index()

print("Average Fluency Scores (1–5):")
print(summary)

# Save summary
summary.to_csv("results/q1_fluency_summary.csv", index=False)
