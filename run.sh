#!/usr/bin/env bash
set -e

echo "[RUN] Q1: Multilingual & Code-Switch"
python src/evaluate_q1.py --config config.yaml

echo "[RUN] Q2: Robustness to Messy Inputs"
python src/evaluate_q2.py --config config.yaml --intervention prompt

echo "[RUN] Q3: Needle-in-a-Haystack"
python src/evaluate_q3.py --config config.yaml

echo "[DONE] See results/ and plots/"
