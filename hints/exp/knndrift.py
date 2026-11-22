#!/usr/bin/env python3
"""knndrift.py A Z (22 Nov): for the goals arm A (a loop started with Z's proofs as its context, e.g. exp54's LAA on Z7) ran
fresh, how Z had run them (runs, the minute of its last run, the places after the nearest proven sibling) and how many
of their kNN lemmas are new since Z's last run (knn_at.tsv), split by whether A's first run proved them."""
import re, collections, statistics as st, sys
A, Z = sys.argv[1], sys.argv[2]   # the new arm (LAA), the old run (Z7)
def runs_to_min(z):
    pts = []
    for line in open(f'loops/{z}.log', errors='replace'):
        m = re.search(r'cascade: (\d+) runs, .*? (\d+)s,', line)
        if m: pts.append((int(m.group(1)), int(m.group(2)) / 60))
    def f(k):
        for r, mi in pts:
            if r >= k: return mi
        return pts[-1][1]
    return f
M = runs_to_min(Z)
zr = collections.defaultdict(list); n = 0
for line in open(f'loops/{Z}/r1/results.tsv', errors='replace'):
    w = line.rstrip('\n').split('\t'); n += 1
    if len(w) > 4: zr[w[0]].append((n, w[4]))
ar = collections.defaultdict(list)
for line in open(f'loops/{A}/r1/results.tsv', errors='replace'):
    w = line.rstrip('\n').split('\t')
    if len(w) > 4: ar[w[0]].append((w[1], w[4]))
first = [g for g, L in ar.items() if L[0][0] == 'THM']
failfirst = [g for g, L in ar.items() if L[0][0] != 'THM']
for lab, G in (('proved at the first run', first), ('failed the first run', failfirst)):
    nr = [len(zr[g]) for g in G]; last = [M(zr[g][-1][0]) for g in G if zr[g]]
    lev = collections.Counter(re.sub(r'@.*', '', zr[g][-1][1]) for g in G if zr[g])
    print(f'{A} goals {lab}: {len(G)}; {Z} runs on them: median {st.median(nr) if nr else 0}, none {sum(1 for x in nr if x == 0)};'
          f' minute of {Z}\'s last run, quartiles {"/".join(f"{v:.0f}" for v in st.quantiles(last, n=4)) if len(last) > 3 else "-"};'
          f' its level: {lev.most_common(5)}')
# places after the nearest proven sibling below, in Z's final state (all goals of the original, by goal number)
sol = set(l.split('\t')[0] for l in open(f'loops/{Z}/solved.tsv', errors='replace'))
byo = collections.defaultdict(list)
for l in open('sets/all'):
    n_ = l.strip()
    if '__goal_' in n_:
        o, k = n_.rsplit('__goal_', 1); byo[o].append((int(k), n_))
gap = {}
for o, L in byo.items():
    L.sort(); last = None
    for i, (k, n_) in enumerate(L):
        if n_ in sol: last = i
        else: gap[n_] = (i - last) if last is not None else 999
for lab, G in (('proved at the first run', first), ('failed the first run', failfirst)):
    c = collections.Counter(min(gap.get(g, -1), 10) for g in G)
    print(f'{A} {lab}: places after the nearest proven sibling in {Z} at its end (10 = 10+):', sorted(c.items()))
def kat(z):
    d = {}
    for l in open(f'loops/{z}/knn_at.tsv', errors='replace'):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 2: d[w[0]] = frozenset(filter(None, w[1].split(',')))
    return d
KZ, KA = kat(Z), kat(A)
for lab, G in (('proved at the first run', first), ('failed the first run', failfirst)):
    ch = [len(KA[g] - KZ[g]) for g in G if g in KZ and g in KA]
    if ch:
        c = collections.Counter(min(x, 10) for x in ch)
        print(f'{A} {lab}: kNN lemmas new since {Z}\'s last run (of {len(ch)} goals; 10 = 10+): median {st.median(ch)},', sorted(c.items()))
for M in (3, 5, 8):
    rows_ = [(len(KA[g] - KZ[g]) >= M, True) for g in first if g in KZ and g in KA] + \
            [(len(KA[g] - KZ[g]) >= M, False) for g in failfirst if g in KZ and g in KA]
    hi = [ok for d, ok in rows_ if d]; lo = [ok for d, ok in rows_ if not d]
    print(f'M={M}: {M}+ new kNN lemmas {sum(hi)} of {len(hi)} proved ({100*sum(hi)/max(1,len(hi)):.0f}%), fewer {sum(lo)} of {len(lo)} ({100*sum(lo)/max(1,len(lo)):.0f}%)')
