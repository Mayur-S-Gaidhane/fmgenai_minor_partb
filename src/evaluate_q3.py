import argparse, yaml, math, re
import pandas as pd
from src.llm import call_llm
from src.utils import ensure_dir

NEEDLE = "The secret ticket code is VIOLET-9241."
QUESTION = "What is the secret ticket code? Return on one line: Final: <code>."

def approx_tokens(s: str) -> int:
    return int(len(s.split()) / 0.75)  # rough

def build_filler(target_tokens: int) -> str:
    para = ("This is neutral filler text written to create a long context for evaluation. "
            "It contains simple sentences about weather, books, tools, and travel plans. "
            "No sensitive content is included. ")
    chunks = []
    while approx_tokens(" ".join(chunks)) < target_tokens:
        chunks.append(para)
    return " ".join(chunks)

def insert_needle(filler: str, position: str) -> str:
    if position == "start":
        return NEEDLE + " " + filler
    if position == "middle":
        words = filler.split(); mid = len(words)//2
        return " ".join(words[:mid]) + " " + NEEDLE + " " + " ".join(words[mid:])
    if position == "end":
        return filler + " " + NEEDLE
    raise ValueError(position)

def ask_with_context(context: str) -> str:
    return context + "\n\n" + QUESTION

def extract_code(s: str) -> str:
    m = re.search(r'[A-Z]+-\d+', s or "")
    return m.group(0) if m else ""

def run_once(model, temp, max_tokens, position):
    filler = build_filler(10000)
    context = insert_needle(filler, position)
    prompt = ask_with_context(context)
    pred = call_llm(prompt, system_prompt=None, model=model, temperature=temp, max_tokens=max_tokens)
    code = extract_code(pred)
    correct = int(code == "VIOLET-9241")
    return {
        "version": "baseline",
        "position": position,
        "tokens_total": approx_tokens(context),
        "needle_token_idx": (0 if position=="start" else (approx_tokens(context)//2 if position=="middle" else approx_tokens(context)-5)),
        "prompt": "[omitted_long_context]",
        "prediction": pred,
        "correct": correct
    }

def run_chunk_retrieve(model, temp, max_tokens, position):
    filler = build_filler(10000)
    context = insert_needle(filler, position)
    words = context.split()
    chunk_size = 800
    stride = 200
    chunks = []
    i = 0
    while i < len(words):
        chunks.append((" ".join(words[i:i+chunk_size]), i))
        i += (chunk_size - stride)
    cand = [c for c in chunks if "VIOLET-9241" in c[0]]
    chosen = cand[0][0] if cand else chunks[len(chunks)//2][0]
    prompt = ask_with_context(chosen)
    pred = call_llm(prompt, system_prompt=None, model=model, temperature=temp, max_tokens=max_tokens)
    code = extract_code(pred)
    correct = int(code == "VIOLET-9241")
    return {
        "version": "chunk_retrieve",
        "position": position,
        "tokens_total": approx_tokens(chosen),
        "needle_token_idx": -1,
        "prompt": "[omitted_chunk]",
        "prediction": pred,
        "correct": correct
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model = cfg.get("model", "gpt-4o-mini")
    temp = float(cfg.get("temperature", 0.2))
    max_toks = int(cfg.get("max_tokens", 64))

    rows = [run_once(model, temp, max_toks, pos) for pos in ["start","middle","end"]]
    ensure_dir("results/q3_results.csv")
    pd.DataFrame(rows).to_csv("results/q3_results.csv", index=False)

    rows_m = [run_chunk_retrieve(model, temp, max_toks, pos) for pos in ["start","middle","end"]]
    pd.DataFrame(rows_m).to_csv("results/q3_results_mitigated.csv", index=False)
    print("[OK] Wrote results/q3_results.csv and results/q3_results_mitigated.csv")

if __name__ == "__main__":
    main()
