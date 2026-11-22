#!/usr/bin/env python3
"""kdbins.py ARM [ARM...] [--root loops] (22 Nov): L0 runs of goals that had run before (retries), by the kd=N field
(loop.py --knn-drift: proofs since the goal's last fresh run that score above its 30th kNN lemma), in bins: runs,
proofs, the proof rate and CPU hours. Rows without kd= (an arm without --knn-drift) count as kd unknown."""
import sys, collections
root = 'loops'; arms = []
it = iter(sys.argv[1:])
for x in it:
    if x == '--root': root = next(it)
    else: arms.append(x)
B = [(0, 0), (1, 2), (3, 4), (5, 9), (10, 10**9)]
def bn(k):
    for lo, hi in B:
        if lo <= k <= hi: return f'{lo}' if lo == hi else (f'{lo}+' if hi > 10**8 else f'{lo}-{hi}')
for a in arms:
    seen = set(); st = collections.defaultdict(lambda: [0, 0, 0.0])
    for line in open(f'{root}/{a}/r1/results.tsv', errors='replace'):
        w = line.rstrip('\n').split('\t')
        if len(w) < 5: continue
        n = w[0]; first = n not in seen; seen.add(n)
        if w[4] != 'L0': continue   # fresh runs at the first level (the @0 variants go the deep way and carry no kd=)
        if first: continue
        kd = next((int(x[3:]) for x in w[6:] if x.startswith('kd=')), None)
        k = 'unknown' if kd is None else bn(kd)
        s = st[k]; s[0] += 1; s[1] += w[1] == 'THM'; s[2] += float(w[2])
    print(f'{a} retries (L0 runs of goals run before), by kd:')
    for k in sorted(st, key=lambda k: (k == 'unknown', int(k.split('-')[0].rstrip('+')) if k != 'unknown' else 0)):
        r, p, c = st[k]
        print(f'  kd {k:>7}: {p:5d}/{r:<6d} {100*p/max(1,r):5.1f}%  {c/3600:6.2f} CPU h  {p/max(1e-9,c/3600):6.1f}/CPU h')
