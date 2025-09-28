# Report Outline (≤8 pages main)

## A. Introduction
Q1 and Q2 .

## B. Methods (common)
Methods of Q1 :

Model: mistral:7b-instruct (via Ollama).

Data: 20 prompts each in English (L1), Marathi (L2), Hinglish (L3), and code-switched (CS).

Metrics: Accuracy (exact match with gold answer) and Fluency (1–5 manual scoring).

Mitigation: “Language pinning” → explicitly instructing the model to always respond in English.

Method of Q2 :

Methods

Model: mistral:7b-instruct via Ollama.

Prompts: 50 clean test items.

Noise types: typos, spacing errors, Unicode confusables, emoji insertions.

Noise levels: low and high distortion.

Metric: Accuracy compared to gold answers.

Mitigation strategy: robust prompting (“ignore typos, extra spaces, and symbols”).





## C. Q1: Multilingual & Code-Switch
Table 1. Q1 Combined (Baseline: Accuracy + Fluency)

Condition	n	Accuracy	CI Low	CI High	Avg Fluency	n Rated
L1EN	20	0.10	0.00	0.20	2.85	13
L2MR	20	0.05	0.00	0.15	3.86	14
L3HINGLISH	20	0.00	0.00	0.00	3.81	16
CSMIXED	20	0.00	0.00	0.00	3.82	17

Table 2. Q1 Mitigated (Language Pinning, 6 samples/condition)

Condition	n	Accuracy	CI Low	CI High
L1EN	6	0.33	0.00	0.67
L2MR	6	0.00	0.00	0.00
L3HINGLISH	6	0.00	0.00	0.00
CSMIXED	6	0.00	0.00	0.00
Analysis

Baseline:

English accuracy was low (10%) but at least non-zero.

Marathi achieved only 5%, while Hinglish and code-switched inputs failed completely (0%).

Fluency scores (~3.5–3.8 across non-English) suggest outputs often sounded natural even when factually wrong, showing a dangerous mismatch between readability and correctness.

Error patterns:

Language drift → responding in Marathi instead of English.

Verbose outputs → long, descriptive text instead of concise answers.

Hallucinations → confident but incorrect answers.

Mitigation (language pinning):

Accuracy in English rose from 10% → 33% (clear improvement).

However, Marathi, Hinglish, and code-switched inputs stayed at 0%, confirming the model’s weaknesses in these contexts are not fixable by prompting alone.

Conclusion

The Q1 evaluation shows a strong accuracy–fluency gap: the model produces fluent but unreliable answers, especially in non-English conditions. While English accuracy improves under language pinning, performance in Marathi, Hinglish, and code-switched prompts remains at 0%, highlighting a serious limitation in multilingual capability. Prompt-based mitigation helps only when the underlying language competence exists (English), but offers no benefit for low-resource or mixed-language cases.

This suggests that for multilingual robustness, model training and data coverage matter more than clever prompting, and evaluation should always check both accuracy and fluency to avoid overestimating model ability.

## D. Q2: Robustness to Messy Inputs
Methods

Model: mistral:7b-instruct via Ollama.

Prompts: 50 clean test items.

Noise types: typos, spacing errors, Unicode confusables, emoji insertions.

Noise levels: low and high distortion.

Metric: Accuracy compared to gold answers.

Mitigation strategy: robust prompting (“ignore typos, extra spaces, and symbols”).

Results

Table 2. Accuracy under Noise Perturbations

Noise Type	High	Low	Clean
Clean	0.36	0.36	0.36
Confusables	0.32	0.44	–
Emoji	0.42	0.36	–
Spacing	0.32	0.34	–
Typos	0.22	0.32	–

Heatmap (Figure 1):
The figure visualizes accuracy by noise type and strength. figure are placed in plots/q2_heatmap.png

Analysis

Baseline: Clean input accuracy was 0.36 (~36%).

Best robustness: Emoji noise had little effect, even slightly increasing accuracy at high noise (0.42). This suggests the model was largely insensitive to added emoji characters.

Confusables: Accuracy improved under low-strength confusables (0.44), but dropped under high distortion (0.32).

Spacing: Performance stayed roughly stable (0.34–0.32), showing mild resilience.

Typos: The model was most fragile here: accuracy fell from 0.32 (low noise) to 0.22 at high typo levels — the largest drop among noise types.

Failure cases (qualitative):

Misreading distorted tokens (e.g., “par1s” → not recognized as “Paris”).

Dropping parts of inputs with confusables.

Treating emoji as semantic tokens in rare cases.

Mitigation impact:
Robust prompting partially helped normalize noise but gains were modest. For typos in particular, mitigation did not recover accuracy to the clean baseline.



## E Reproducibility

- One-command run via `bash run.sh`
- CSVs with per-example predictions
- Minimal configs checked in
- Methods templates in `report/report_outline.md`

# session env (or use setx to make permanent)
$env:PROVIDER="ollama"
$env:OLLAMA_MODEL="mistral:7b-instruct"

# Q1 baseline (20 items × 4 conditions = 80 calls) it takes 40 min to run in my local system execution speed depend on GPU/CPU 
python -m src.evaluate_q1 --config config.yaml

# Q1 mitigation re-test (6 items/condition) it takes 15 min to run in my local system execution speed depend on GPU/CPU 
python -m src.evaluate_q1 --config config.yaml --mitigate

# Q2 full (50 clean + noisy variants (4 types × 2 levels × 50 each)= 450 calls ) it takes 60 min to run in my local system execution speed depend on GPU/CPU 
python -m src.evaluate_q2 --config config.yaml --intervention prompt

# quick test for Q2 ()
python -m src.evaluate_q2 --config config.yaml --intervention prompt --quick

# (optional alt) use preprocessing instead of prompt:
# python -m src.evaluate_q2 --config config.yaml --intervention preprocess

# full run Q1 and Q2 together :
.\run.bat

# Fluemcy analysis 
python fluency_sampler.py     --- Print out 10 rows per condition in the terminal to check fluency

python fluency_avg.py         --- This gives you a clean table output of Avg_fluency 

python test.py                --- To check what flency score read by pandas if fluency score none .

python fluency_probe_and_avg.py --- it will list out 6 columes value to in first 5 row in q1_results.csv

python merge_q1_tables.py     --- It is combine output table of q1_summary.csv and q1_fluency_summary.csv.

## F. References
Ollama : version is 0.12.3 and Model: mistral:7b-instruct.
CHATGPT : GPT-5 
github : 
