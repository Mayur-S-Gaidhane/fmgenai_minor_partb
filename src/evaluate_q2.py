import argparse, yaml, random, csv, math, re, sys
from pathlib import Path
from unidecode import unidecode
import numpy as np
import pandas as pd
from src.llm import call_llm
from src.utils import exact_match, ensure_dir

# -----------------------
# Data generation (50 clean items)
# -----------------------
def generate_clean_items():
    items = []
    idc = 1

    # Capitals (10)
    capitals = {
        "France": "Paris","Japan": "Tokyo","Australia": "Canberra","Canada": "Ottawa","Brazil": "Brasilia",
        "India": "New Delhi","Italy": "Rome","Kenya": "Nairobi","Spain": "Madrid","Egypt": "Cairo",
    }
    for country, cap in capitals.items():
        prompt = f"What is the capital of {country}? Answer in one word."
        items.append((idc, "capitals", prompt, cap)); idc += 1

    # Arithmetic (10)
    pairs = [(247,58),(13,4),(91,9),(36,7),(125,25),(64,8),(72,9),(19,11),(123,77),(45,5)]
    for a,b in pairs:
        prompt = f"Compute {a} + {b}. Return only the final number."
        items.append((idc, "arithmetic_add", prompt, str(a+b))); idc += 1

    # Min of list (10)
    lists = [[12,3,18],[7,2,9],[100,99,101],[5,5,6],[0,10,1],[42,11,43],[3,3,3],[8,1,8],[15,14,16],[99,9,19]]
    for arr in lists:
        prompt = f"Find the minimum of these numbers: {', '.join(map(str,arr))}. Return only the number."
        items.append((idc, "min_list", prompt, str(min(arr)))); idc += 1

    # Sentiment (10)
    sents = [
        ("I love this product", "Positive"),("This is terrible", "Negative"),
        ("Absolutely fantastic!", "Positive"),("Not good at all", "Negative"),
        ("I really enjoyed it", "Positive"),("I hate this", "Negative"),
        ("It was okay", "Positive"),("Awful experience", "Negative"),
        ("Superb quality", "Positive"),("Bad and disappointing", "Negative"),
    ]
    for text, lab in sents:
        prompt = f"Classify the sentiment of the sentence '{text}' as Positive or Negative. Return only 'Positive' or 'Negative'."
        items.append((idc, "sentiment", prompt, lab)); idc += 1

    # String ops (10)
    ops = [
        ("Reverse the letters of 'CAT'.", "TAC"),
        ("Return the first three letters of 'Elephant'.", "Ele"),
        ("Count the vowels in 'Education'. Return only the number.", "5"),
        ("Convert 7:05 PM to 24-hour format HH:MM.", "19:05"),
        ("Sort ascending: 7, 2, 9. Return as '2,7,9'.", "2,7,9"),
        ("Is 0 even or odd? Return 'even' or 'odd'.", "even"),
        ("Multiply 13 × 4. Return only the final number.", "52"),
        ("Convert 25°C to Fahrenheit. Return only the integer.", "77"),
        ("Next day after 2025-02-28 in YYYY-MM-DD.", "2025-03-01"),
        ("How many words are in 'Hello world from AI'? Return only the number.", "4"),
    ]
    for p, g in ops:
        items.append((idc, "string_ops", p, g)); idc += 1

    assert len(items) == 50
    return items

# -----------------------
# Noise generation
# -----------------------
QWERTY_ADJ = {
  'a':'qs','b':'vn','c':'vx','d':'sf','e':'wr','f':'dg','g':'fh','h':'gj','i':'uo','j':'hk',
  'k':'jl','l':'k','m':'n','n':'bm','o':'ip','p':'o','q':'wa','r':'et','s':'ad','t':'ry',
  'u':'yi','v':'cb','w':'qe','x':'zc','y':'tu','z':'x','0':'9o','1':'2q','2':'13w','3':'24e',
  '4':'35r','5':'46t','6':'57y','7':'68u','8':'79i','9':'80o'
}
CONFUSABLES = {'a':'α','e':'е','o':'ο','i':'і','p':'р','c':'с','0':'O','O':'0','-':'—'}
EMOJI = ["🙂","⭐","✅","📌","🔹","✨"]

def add_typos(s, strength="low"):
    prob = 0.03 if strength=="low" else 0.08
    out = []
    for ch in s:
        if ch.lower() in QWERTY_ADJ and random.random() < prob:
            out.append(random.choice(QWERTY_ADJ[ch.lower()]))
        else:
            out.append(ch)
    ins_prob = 0.01 if strength=="low" else 0.03
    i = 0; res = []
    while i < len(out):
        res.append(out[i])
        if random.random() < ins_prob and out[i].isalpha():
            res.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
        i += 1
    return "".join(res)

def add_spacing_punct(s, strength="low"):
    out = []
    for ch in s:
        if ch in ",." and random.random() < (0.5 if strength=="high" else 0.2):
            continue
        out.append(ch)
        if ch == " " and random.random() < (0.2 if strength=="high" else 0.05):
            out.append("  ")
    return "".join(out)

def add_confusables(s, strength="low"):
    prob = 0.03 if strength=="low" else 0.08
    out = []
    for ch in s:
        if ch in CONFUSABLES and random.random() < prob:
            out.append(CONFUSABLES[ch])
        else:
            out.append(ch)
    if strength == "high":
        out = [(" " + c + " ") if c in ":;=+-" else c for c in out]
        out = "".join(out)
    else:
        out = "".join(out)
    return out

def sprinkle_emoji(s, strength="low"):
    prob = 0.02 if strength=="low" else 0.06
    tokens = s.split(" ")
    for i in range(len(tokens)):
        if random.random() < prob:
            tokens[i] = tokens[i] + " " + random.choice(EMOJI)
    return " ".join(tokens)

def perturb(s, noise_type, level):
    if noise_type == "typos": return add_typos(s, level)
    if noise_type == "spacing": return add_spacing_punct(s, level)
    if noise_type == "confusables": return add_confusables(s, level)
    if noise_type == "emoji": return sprinkle_emoji(s, level)
    raise ValueError(noise_type)

# -----------------------
# Robust prompting template
# -----------------------
ROBUST_PROMPT_PREFIX = (
    "You may see typos, odd spacing or Unicode confusables. Normalize mentally and focus on semantic intent. "
    "Follow the task exactly and output only the requested final value.\n\n"
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--intervention", choices=["prompt","preprocess"], default="prompt",
                    help="Use robust prompting template OR light preprocessing.")
    ap.add_argument("--quick", action="store_true",
                    help="Quick mode: run only first 5 items (≈45 calls) instead of full 50 (≈450 calls).")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model = cfg.get("model", "gpt-4o-mini")  # ignored for PROVIDER=ollama
    temp = float(cfg.get("temperature", 0.2))
    max_toks = int(cfg.get("max_tokens", 64))

    clean_all = generate_clean_items()
    clean = clean_all[:5] if args.quick else clean_all
    print(f"[Q2] Starting evaluation | intervention={args.intervention} | items={len(clean)} "
          f"({'QUICK' if args.quick else 'FULL'})")

    # Save clean prompts used (for reproducibility)
    pd.DataFrame(clean, columns=["id","task","prompt_in","gold"]).to_csv("data/q2_clean.csv", index=False)

    rows = []

    # -----------------------
    # Clean baseline
    # -----------------------
    print(f"[Q2] Clean baseline: {len(clean)} items")
    for idx, (rid, task, prompt, gold) in enumerate(clean, start=1):
        print(f"[Q2] CLEAN | id={rid} ({idx}/{len(clean)}) ... ", end="", flush=True)
        pred = call_llm(prompt, system_prompt=None, model=model, temperature=temp, max_tokens=max_toks)
        print("✓", flush=True)
        rows.append({"id": rid, "noise_type": "clean", "noise_level": "na", "prompt_in": prompt,
                     "gold": gold, "pred": pred, "correct": int(exact_match(pred, gold))})

    # -----------------------
    # Perturbations
    # -----------------------
    noise_types = ["typos","spacing","confusables","emoji"]
    levels = ["low","high"]
    for noise in noise_types:
        for level in levels:
            print(f"[Q2] Noise='{noise}' level='{level}': {len(clean)} items")
            for idx, (rid, task, prompt, gold) in enumerate(clean, start=1):
                noisy = perturb(prompt, noise, level)
                if args.intervention == "prompt":
                    final_input = ROBUST_PROMPT_PREFIX + noisy
                    sys_prompt = None
                else:
                    final_input = " ".join(unidecode(noisy).split())
                    sys_prompt = None
                print(f"[Q2] {noise.upper()}:{level} | id={rid} ({idx}/{len(clean)}) ... ", end="", flush=True)
                pred = call_llm(final_input, system_prompt=sys_prompt, model=model, temperature=temp, max_tokens=max_toks)
                print("✓", flush=True)
                rows.append({"id": rid, "noise_type": noise, "noise_level": level, "prompt_in": noisy,
                             "gold": gold, "pred": pred, "correct": int(exact_match(pred, gold))})

    ensure_dir("results/q2_results.csv")
    res_df = pd.DataFrame(rows)
    res_df.to_csv("results/q2_results.csv", index=False)

    # Heatmap-style table
    pivot = res_df.groupby(["noise_type","noise_level"])["correct"].mean().reset_index()
    pivot = pivot.pivot(index="noise_type", columns="noise_level", values="correct")
    clean_acc = res_df[res_df.noise_type=="clean"]["correct"].mean()
    for lvl in ["low","high"]:
        pivot.loc["clean", lvl] = clean_acc
    pivot.sort_index(inplace=True)
    pivot.to_csv("results/q2_heatmap_table.csv")

    # Plot (matplotlib, single chart, default colors)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Accuracy by Noise Type/Strength (incl. clean baseline)")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i,j]
            if isinstance(val, float):
                ax.text(j, i, f"{val:.2f}", ha='center', va='center')
    fig.tight_layout()
    fig.savefig("plots/q2_heatmap.png", dpi=200)
    plt.close(fig)

    print("[Q2][OK] Wrote: results/q2_results.csv")
    print("[Q2][OK] Wrote: results/q2_heatmap_table.csv")
    print("[Q2][OK] Wrote: plots/q2_heatmap.png")

if __name__ == "__main__":
    main()
