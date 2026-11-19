#!/usr/bin/env python3
"""exp21/ana.py [RES]: per arm (and P9 from out_P9/results.tsv), on the goals every arm has run (complete goals): proved, proved and not by C, CPU h,
new per CPU h; then the greedy union curve by new proofs per CPU hour, starting from C."""
import collections, sys
res = sys.argv[1] if len(sys.argv) > 1 else 'res_A.tsv'
R = collections.defaultdict(dict)
for l in open(res):
    w = l.rstrip('\n').split('\t')
    a, g = w[0].split(':', 1); R[g][a] = (w[1] == '1', float(w[2]))
arms = ['C', 'K60', 'U', 'S', 'R2', 'N', 'G', 'X']
try:   # (the Prover9 arm: p9twee.py batch results, goal, THM/NO, seconds)
    for l in open('out_P9/results.tsv'):
        w = l.rstrip('\n').split('\t')
        if w[0] in R:
            R[w[0]]['P9'] = (w[1] == 'THM', float(w[2]))
    arms.append('P9')
except OSError:
    pass
G = [g for g in R if all(a in R[g] for a in arms)]
print(f'{len(G)} complete goals of {len(R)} started')
P = {a: {g for g in G if R[g][a][0]} for a in arms}
cpu = {a: sum(R[g][a][1] for g in G) / 3600 for a in arms}
for a in arms:
    new = P[a] - P['C']
    print(f'{a:4} proved {len(P[a]):3}  not by C {len(new):3}  lost {len(P["C"] - P[a]):3}  CPU h {cpu[a]:5.2f}  '
          f'proofs/CPU h {len(P[a]) / max(cpu[a], 1e-9):5.1f}  new/CPU h {len(new) / max(cpu[a], 1e-9):5.1f}')
cov = set(P['C']); tot = cpu['C']; left = [a for a in arms if a != 'C']
print(f'greedy: C {len(cov)} at {tot:.2f} CPU h')
while left:
    b = max(left, key=lambda a: len(P[a] - cov) / max(cpu[a], 1e-9))
    n = len(P[b] - cov); cov |= P[b]; tot += cpu[b]; left.remove(b)
    print(f'  + {b}: +{n} -> {len(cov)} at {tot:.2f} CPU h')
