#!/usr/bin/env python3
"""quickfinal_stats.py [--from LINE] [--cap S]: exp83's motivation figures (24 Nov, notes/2026-11-24-quick-finals.md).

From loops/CLS71.log (from LINE on, default 1047, the 08:59 instance) and loops/CLS71/climb.tsv: the climber's finished
targets, the CPU seconds of its proving finals (quartiles, how many under CAP, default 40), the median CPU of its failed
finals; the proof rate by proof-line distance to the nearest goal of the original proved before (abs/goal_lines.tsv,
loops/UL/solved.tsv order); and production's failed runs on the proved targets before the climber's proof
(loops/UL/r5/results.tsv: runs per goal, labels, CPU h)."""
import collections, re, sys
H = '/project/hintwork'
A = sys.argv[1:]
FROM = int(A[A.index('--from') + 1]) if '--from' in A else 1047
CAP = float(A[A.index('--cap') + 1]) if '--cap' in A else 40.0
L = open(f'{H}/loops/CLS71.log').read().splitlines()[FROM - 1:]
fin_log = [(m.group(1), m.group(2) == 'THM') for l in L for m in [re.match(r'(\S+__goal_\d+) (THM|NO) ', l)] if m]
th = {g for g, ok in fin_log if ok}
no = {g for g, ok in fin_log if not ok}
fin = {}
for l in open(f'{H}/loops/CLS71/climb.tsv'):
    w = l.split('\t')
    if len(w) > 5 and w[1] == 'final':
        fin[w[0]] = (w[3], float(w[5]))
t = sorted(fin[g][1] for g in th if g in fin and fin[g][0] == 'THM')
n = len(t)
print(f'finished {len(fin_log)}, proved {len(th)}; proved by the final {n}')
if n:
    print('proving finals CPU s: q25 %.0f, median %.0f, q75 %.0f, q90 %.0f; under %.0f s: %d' % (
        t[n // 4], t[n // 2], t[3 * n // 4], t[int(0.9 * (n - 1))], CAP, sum(x < CAP for x in t)))
nf = sorted(fin[g][1] for g in no if g in fin)
if nf:
    print(f'failed finals {len(nf)}, median CPU s {nf[len(nf) // 2]:.0f}')
gl = {l.split()[0]: int(l.split()[1]) for l in open(f'{H}/abs/goal_lines.tsv')}
order = [l.split('\t')[0] for l in open(f'{H}/loops/UL/solved.tsv') if l.strip()]
pos = {g: i for i, g in enumerate(order)}
by = collections.defaultdict(list)
for g in gl:
    o, k = g.rsplit('__goal_', 1)
    by[o].append(int(k))
cur = 0
rows = []
for g, ok in fin_log:
    if ok and g in pos:
        cur = max(cur, pos[g])
    lim = pos[g] if ok and g in pos else cur
    o, k = g.rsplit('__goal_', 1)
    k = int(k)
    below = [j for j in by[o] if j < k and pos.get(f'{o}__goal_{j}', 10 ** 9) < lim]
    rows.append((gl[g] - gl[f'{o}__goal_{max(below)}'] if below and g in gl else 10 ** 6, ok))
for a, b in ((0, 20), (20, 40), (40, 80), (80, 160), (160, 10 ** 7)):
    r = [x for x in rows if a <= x[0] < b]
    if r:
        print(f'distance {a}-{b if b < 10 ** 7 else "more"} lines: finished {len(r)}, proved {sum(x[1] for x in r)}'
              f' ({100 * sum(x[1] for x in r) / len(r):.0f}%)')
pr = collections.defaultdict(list)
for l in open(f'{H}/loops/UL/r5/results.tsv'):
    w = l.split('\t', 6)
    if w[0] in th and len(w) > 4 and w[1] != 'THM':
        try:
            s = float(w[2])
        except ValueError:
            s = 0.0
        pr[w[0]].append((w[4], s))
k = sorted(len(pr[g]) for g in th)
lab = collections.Counter(x[0] for g in th for x in pr[g])
deep = sum(v for x, v in lab.items() if not (x == 'L0' or x.endswith('@0')))
print(f'production before: failed runs per proved goal median {k[len(k) // 2] if k else 0}, max {max(k) if k else 0};'
      f' CPU h {sum(x[1] for g in th for x in pr[g]) / 3600:.1f}; runs beyond the 5 s level {deep}')
print('  labels', lab.most_common(6))
allf = [fin[g][1] for g, _ in fin_log if g in fin]
print(f'all finals CPU h {sum(allf) / 3600:.1f}; the same finals capped at {CAP:.0f} s {sum(min(x, CAP) for x in allf) / 3600:.1f}')
