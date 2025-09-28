import pandas as pd
import random

# Load your results
df = pd.read_csv("results/q1_results.csv")

# For each condition, sample 10 rows
conditions = df['condition'].unique()
for cond in conditions:
    subset = df[df['condition'] == cond]
    sample = subset.sample(min(10, len(subset)), random_state=42)
    print(f"\n--- {cond} ---")
    for _, row in sample.iterrows():
        print(f"ID={row['id']} | Prompt={row['prompt']}")
        print(f"Prediction={row['prediction']}")
        print("Fluency: [ ]\n")
