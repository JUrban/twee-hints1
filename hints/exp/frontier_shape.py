"""(24 Nov, exp82 context; notes/2026-11-24-horn-lemmas.md) Run from /project/hintwork. Local heads and HLW1 runs by proof-line
distance (LADR "% goal_N line_L") to the nearest proven goal below; near heads run history; holes (a later goal of the
same original proved) against tails."""
import collections, re, os
L = {}
for f in os.listdir('/project/AIM60k/problems/ladr'):
    if '__goal_' not in f: continue
    m = None
    with open('/project/AIM60k/problems/ladr/' + f) as fh:
        for l in fh:
            m = re.search(r'% goal_\d+\s+line_(\d+)', l)
            if m: break
    if m: L[f] = int(m.group(1))
T = {l.split('\t')[0] for l in open('loops/UL/solved.tsv') if l.strip()}
by = collections.defaultdict(list)
for g in L:
    o, k = g.rsplit('__goal_', 1); by[o].append((int(k), g))
dist = {}; heads = []
for o, v in by.items():
    v.sort()
    for i, (k, g) in enumerate(v):
        if g in T: continue
        below = [L[h] for _, h in v[:i] if h in T]
        dist[g] = L[g] - max(below) if below else L[g]
        if i == 0 or v[i-1][1] in T: heads.append(g)
bins = [(0, 8), (9, 13), (14, 21), (22, 34), (35, 55), (56, 144), (145, 10**9)]
def b(x):
    for lo, hi in bins:
        if lo <= x <= hi: return f'{lo}-{hi if hi < 10**9 else ""}'
print('goals with lines', len(L), 'unsolved', len(dist), 'local heads', len(heads))
c = collections.Counter(b(dist[g]) for g in heads)
H = {}
for l in open('cond/HLW1/results.tsv'):
    w = l.split('\t')
    if w[1] in ('THM', 'NO'): H[w[0]] = w[1]
# HLW1 proofs are now in T; take their distance at the time from the snapshot: recompute with T minus HLW1 proofs
T0 = T - {g for g, r in H.items() if r == 'THM'}
def d0(g):
    o, k = g.rsplit('__goal_', 1); k = int(k)
    below = [L[h] for kk, h in by[o] if kk < k and h in T0]
    return L[g] - max(below) if below else L[g]
hb = collections.Counter((b(d0(g)), r) for g, r in H.items())
print('%-10s %6s %10s' % ('lines', 'heads', 'HLW1 THM/run'))
for lo, hi in bins:
    k = f'{lo}-{hi if hi < 10**9 else ""}'
    print('%-10s %6d %6d/%d' % (k, c[k], hb[(k, 'THM')], hb[(k, 'THM')] + hb[(k, 'NO')]))
near = [g for g in heads if 9 <= dist[g] <= 13]
LH = {l.strip() for l in open('sets/localheads71') if l.strip()}
runs = collections.Counter(); best = collections.defaultdict(float); kinds = collections.defaultdict(collections.Counter)
for l in open('loops/UL/r5/results.tsv'):
    w = l.split('\t')
    if len(w) > 4 and w[0] in dist:
        runs[w[0]] += 1
        try: best[w[0]] = max(best[w[0]], float(w[2]))
        except ValueError: pass
        kinds[w[0]][w[4].split('@')[0]] += 1
PL = collections.Counter()
import glob
for f in glob.glob('cond/*/results.tsv'):
    for l in open(f):
        w = l.split('\t')
        if len(w) > 1 and w[0] in dist and w[1] in ('NO', 'THM'): PL[w[0]] += 1
print('near heads', len(near), 'in localheads71', sum(g in LH for g in near))
print('production runs: median', sorted(runs[g] for g in near)[len(near)//2], 'zero', sum(runs[g] == 0 for g in near),
      '| cond runs: median', sorted(PL[g] for g in near)[len(near)//2], 'zero', sum(PL[g] == 0 for g in near))
print('originals:', collections.Counter(g.rsplit('__goal_', 1)[0] for g in near).most_common(8))
for g in near[:6]: print(' ', g, dist[g], 'prod', runs[g], 'cond', PL[g], dict(kinds[g].most_common(3)))
hole = {}
for o, v in by.items():
    last = max((i for i, (k, g) in enumerate(v) if g in T), default=-1)
    for i, (k, g) in enumerate(v):
        if g not in T: hole[g] = i < last
print('unsolved: holes (a proven goal after) %d, tails %d' % (sum(hole.values()), sum(not x for x in hole.values())))
print('local heads: holes %d, tails %d' % (sum(hole[g] for g in heads), sum(not hole[g] for g in heads)))
tl = collections.Counter(g.rsplit('__goal_', 1)[0] for g in hole if not hole[g])
print('tail originals', len(tl), 'tail sizes top', tl.most_common(5))
pr = collections.Counter(hole.get(g, "proved") for g, r in H.items() if r == "NO")
print("HLW1 failures now hole/tail/proved since", pr[True], pr[False], pr["proved"])
