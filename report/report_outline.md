# Report Outline (≤8 pages main)

## A. Introduction
Briefly state what each experiment tests and why it matters.

## B. Methods (common)
Model name/version; decoding settings; hardware/API; seeds/configs; safety.

## C. Q1: Multilingual & Code-Switch
Languages; dataset; scoring (EM + fluency 1–5 on a 10-item subset); mitigation (language pinning); tables with accuracy & 95% CI; 3 failure cases (diagnosis).

## D. Q2: Robustness to Messy Inputs
Task; noise types & strengths; metrics; intervention (prompt or preprocess); heatmap; error taxonomy (3–5 categories).

## E. Q3: Needle-in-a-Haystack
Long context length; positions (start/middle/end); exact-match metric; mitigation (chunk+retrieve) with mini before/after table.

## F. Results & Discussion
Key deltas, insights, limitations.

## G. Reproducibility
Run commands, seeds, CSVs, configs.

## H. References
Cite any sources/libraries/LLMs.
