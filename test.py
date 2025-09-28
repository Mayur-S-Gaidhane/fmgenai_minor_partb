import pandas as pd

df = pd.read_csv("results/q1_results.csv")

# Show first 20 rows with fluency
print(df[['condition', df.columns[-1]]].head(20))

# Show unique raw values in fluency
print("\nUnique values in fluency column:")
print(df[df.columns[-1]].unique())
