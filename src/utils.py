import re, os, random, math
from typing import List

ALNUM_RE = re.compile(r'[^A-Za-z0-9]')

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip().replace('\n', ' ').lower()
    s = ALNUM_RE.sub('', s)
    return s

def exact_match(pred: str, gold: str) -> int:
    return int(normalize_text(pred) == normalize_text(gold))

def f1_score(pred: str, gold: str) -> float:
    p = re.findall(r'[A-Za-z0-9]+', (pred or "").lower())
    g = re.findall(r'[A-Za-z0-9]+', (gold or "").lower())
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    p_set, g_set = set(p), set(g)
    tp = len(p_set & g_set)
    if tp == 0:
        return 0.0
    precision = tp / len(p_set)
    recall = tp / len(g_set)
    return 2 * precision * recall / (precision + recall)

def bootstrap_ci(acc_list: List[int], iters: int = 2000, alpha: float = 0.05):
    if not acc_list:
        return (0.0, 0.0)
    import random
    n = len(acc_list)
    samples = []
    for _ in range(iters):
        samp = [acc_list[random.randrange(n)] for __ in range(n)]
        samples.append(sum(samp)/n)
    samples.sort()
    lo_idx = int(alpha/2 * iters)
    hi_idx = int((1 - alpha/2) * iters)
    return (samples[lo_idx], samples[min(hi_idx, iters-1)])

def ensure_dir(p: str):
    os.makedirs(os.path.dirname(p), exist_ok=True)
