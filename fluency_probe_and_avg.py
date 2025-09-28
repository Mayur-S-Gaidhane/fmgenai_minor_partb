import csv, re
from collections import defaultdict

IN = "results/q1_results.csv"
OUT = "results/q1_fluency_summary.csv"

# --- 1) Inspect header and show a couple of rows' tail cells
with open(IN, "r", encoding="utf-8", newline="") as f:
    rdr = csv.reader(f)
    rows = list(rdr)

if not rows:
    print("No rows found.")
    raise SystemExit(1)

header = rows[0]
print("Detected header columns:")
for i, h in enumerate(header):
    print(f"{i:>2}: {repr(h)}")

print("\nFirst 5 data rows: show last 6 cells (repr)")
for r in rows[1:6]:
    tail = r[-6:] if len(r) >= 6 else r
    print([repr(x) for x in tail])

# --- 2) Compute averages by scanning RIGHTMOST numeric 1..5 per row
num_pat = re.compile(r"^\s*([1-5])\s*$")

totals = defaultdict(float)
counts = defaultdict(int)

cond_idx = None
# try to find 'condition' column robustly
for i, h in enumerate(h.strip().lower() for h in header):
    if h == "condition":
        cond_idx = i
        break
if cond_idx is None:
    print("\nERROR: No 'condition' column found in header; cannot proceed.")
    raise SystemExit(1)

bad = 0
for r in rows[1:]:
    if not r:
        continue
    # pad row to header length (prevents index errors)
    if len(r) < len(header):
        r = r + [""] * (len(header) - len(r))

    cond = r[cond_idx].strip()
    if not cond:
        bad += 1
        continue

    # scan from rightmost non-empty cell
    chosen = None
    for cell in reversed(r):
        if cell is None:
            continue
        s = str(cell).strip().strip(",")
        m = num_pat.match(s)
        if m:
            chosen = int(m.group(1))
            break

    if chosen is None:
        continue

    totals[cond] += chosen
    counts[cond] += 1

print("\nAverage Fluency Scores (1–5):")
if not counts:
    print("(No rows had a rightmost 1–5 value. Check that you saved plain numbers in the last field.)")
else:
    print("condition,avg_fluency,n_rated")
    for cond in sorted(counts):
        avg = totals[cond] / counts[cond]
        print(f"{cond},{avg:.2f},{counts[cond]}")

    # write CSV
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "avg_fluency", "n_rated"])
        for cond in sorted(counts):
            avg = totals[cond] / counts[cond]
            w.writerow([cond, f"{avg:.4f}", counts[cond]])

    print(f"\n[OK] Wrote {OUT}")
