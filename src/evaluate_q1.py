import argparse, yaml, csv, sys, time
from pathlib import Path
import pandas as pd
from src.llm import call_llm
from src.utils import exact_match, bootstrap_ci, ensure_dir

# Conditions: English (L1), Marathi (L2), Hinglish (L3), Code-Switch (CS)
LANG_KEYS = ["L1_en", "L2_mr", "L3_hinglish", "CS_mixed"]

def load_config(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_condition(rows, cond_key, model, temp, max_tokens, system_prompt=None):
    out_rows = []
    total = len(rows)
    print(f"[Q1] Running condition={cond_key} on {total} items ...")
    for idx, r in enumerate(rows, start=1):
        prompt = r[cond_key]
        # --- progress line before call (helps if a call hangs)
        print(f"[Q1] {cond_key} | id={r['id']:>2} ({idx:>2}/{total}) ... ", end="", flush=True)
        pred = call_llm(prompt, system_prompt=system_prompt, model=model,
                        temperature=temp, max_tokens=max_tokens)
        # --- progress success mark
        print("✓", flush=True)

        gold = r["gold_en"]
        acc = exact_match(pred, gold)
        out_rows.append({
            "id": r["id"],
            "condition": cond_key.replace("_", "").upper(),
            "prompt": prompt,
            "gold": gold,
            "prediction": pred,
            "correct": int(acc),
            "fluency": ""  # manual 1–5 rating for a 10-item subset per condition
        })
    return out_rows

def summarize(rows):
    # rows: list of dicts with condition and correct
    by_cond = {}
    for r in rows:
        c = r["condition"]
        by_cond.setdefault(c, []).append(r["correct"])
    summary = []
    for c, vals in by_cond.items():
        acc = sum(vals)/len(vals)
        lo, hi = bootstrap_ci(vals)  # ~95% CI
        summary.append({"condition": c, "n": len(vals), "accuracy": acc, "ci_lo": lo, "ci_hi": hi})
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--mitigate", action="store_true",
                    help="Use language pinning system prompt (re-test 6 items).")
    args = ap.parse_args()

    cfg = load_config(args.config)
    model = cfg.get("model", "gpt-4o-mini")  # ignored for PROVIDER=ollama
    temp = float(cfg.get("temperature", 0.2))
    max_toks = int(cfg.get("max_tokens", 64))

    # Load data
    data_path = Path("data/q1_prompts.csv")
    if not data_path.exists():
        print(f"[Q1][ERROR] Missing data file: {data_path}.", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(data_path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            r["id"] = int(r["id"])
            rows.append(r)

    # Run
    results = []
    if args.mitigate:
        print("[Q1] Mitigation mode: language pinning system prompt on first 6 items per condition")
        system_prompt = "You are a precise assistant. Answer ONLY in English; follow the output format; if unsure say 'unsure'."
        subset = rows[:6]
        for key in LANG_KEYS:
            results += run_condition(subset, key, model, temp, max_toks, system_prompt=system_prompt)
        out_csv = "results/q1_results_mitigated.csv"
        sum_csv = "results/q1_summary_mitigated.csv"
    else:
        print("[Q1] Baseline mode: running all items per condition")
        for key in LANG_KEYS:
            results += run_condition(rows, key, model, temp, max_toks, system_prompt=None)
        out_csv = "results/q1_results.csv"
        sum_csv = "results/q1_summary.csv"

    ensure_dir(out_csv)
    pd.DataFrame(results).to_csv(out_csv, index=False)

    summary = summarize(results)
    pd.DataFrame(summary).to_csv(sum_csv, index=False)

    print(f"[Q1][OK] Wrote: {out_csv}")
    print(f"[Q1][OK] Wrote: {sum_csv}")

if __name__ == "__main__":
    main()
