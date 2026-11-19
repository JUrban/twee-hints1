# (19 Nov) Per-original member yields: does P(proof | label, original), shrunk toward P(proof | label), predict later
# runs better than P(proof | label)? Chronological split of production's rows. Log-loss per test row, and the AUC
# within each label (does the original-level estimate rank a label's runs?).
import sys, math, collections
f_, R, S = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows = []
for i, l in enumerate(open(f_), 1):
    if i < R: continue
    f = l.rstrip('\n').split('\t')
    if len(f) < 5: continue
    rows.append((i, f[4], f[0].rsplit('__goal_', 1)[0], 1 if f[1] != 'NO' else 0))
tr = [r for r in rows if r[0] < S]; te = [r for r in rows if r[0] >= S]
kl = collections.Counter(); nl = collections.Counter(); ko = collections.Counter(); no = collections.Counter()
ka = sum(r[3] for r in tr); na = len(tr)
for _, l, o, y in tr:
    kl[l] += y; nl[l] += 1; ko[(l, o)] += y; no[(l, o)] += 1
def p_lab(l): return (kl[l] + 1 * ka / na) / (nl[l] + 1)
def p_fam(l, o, m): return (ko[(l, o)] + m * p_lab(l)) / (no[(l, o)] + m)
res = collections.defaultdict(float)
for _, l, o, y in te:
    for name, p in [('label', p_lab(l))] + [(f'label x original, m={m}', p_fam(l, o, m)) for m in (5, 20, 100)]:
        p = min(max(p, 1e-4), 1 - 1e-4)
        res[name] -= y * math.log(p) + (1 - y) * math.log(1 - p)
print('train rows', len(tr), 'test rows', len(te), 'test proofs', sum(r[3] for r in te))
for k, v in res.items(): print(f'  {k}: log-loss {v / len(te):.5f}')
# within-label ranking: AUC of p_fam(m=20) among each label's test runs, pooled by label (weighted by label's pairs)
from itertools import groupby
tot_pairs = 0; tot_auc = 0.0
for l in set(r[1] for r in te):
    T = [(p_fam(l, o, 20), y) for _, l2, o, y in te if l2 == l]
    pos = [p for p, y in T if y]; neg = [p for p, y in T if not y]
    if not pos or not neg: continue
    neg.sort(); import bisect
    a = sum(bisect.bisect_left(neg, p) + 0.5 * (bisect.bisect_right(neg, p) - bisect.bisect_left(neg, p)) for p in pos)
    tot_auc += a; tot_pairs += len(pos) * len(neg)
    if len(pos) >= 10: print(f'  {l}: test runs {len(T)} proofs {len(pos)} AUC by original {a / (len(pos) * len(neg)):.3f}')
print('  pooled within-label AUC', round(tot_auc / tot_pairs, 3))
