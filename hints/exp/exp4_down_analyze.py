#!/usr/bin/env python3
"""exp4/down_analyze.py DOWN.tsv [T]: the down runs with sketch hints against exp3's deep runs of the same goals.
A deep run of 320 abstract s counts as proved within T (default 80) when its proof took at most 2000 T pairs."""
import collections, os, re, sys
T = float(sys.argv[2]) if len(sys.argv) > 2 else 80
down = collections.defaultdict(dict)
for l in open(sys.argv[1]):
    w = l.rstrip('\n').split('\t'); down[w[1]][w[0]] = w
deep = {}
for arm in 'CKEV':
    p = f'/project/hintwork/exp3/res_{arm}@320.tsv'
    deep[arm] = {w[0]: w for w in (l.rstrip('\n').split('\t') for l in open(p))} if os.path.exists(p) else {}
for arm, rs in sorted(down.items()):
    pr = sorted(g for g, w in rs.items() if w[4] == '1')
    print(f'{arm}: {len(rs)} goals, proved {len(pr)}', ' '.join(f'{g}@{int(rs[g][6])//2000}s' for g in pr))
    for d in 'CKEV':
        both = [g for g in rs if g in deep[d]]
        dp = [g for g in both if deep[d][g][1] == '1']
        dT = [g for g in dp if int(deep[d][g][4]) <= 2000 * T]
        new = [g for g in pr if g in deep[d] and deep[d][g][1] != '1']
        print(f'   vs {d}@320 on {len(both)} common: {d} proved {len(dp)} ({len(dT)} within {T:g} s); {arm} proved '
              f'{sum(g in pr for g in both)}, of them unproved by {d}@320: {len(new)} {" ".join(new)}')
    m = [int(w[3]) for w in rs.values()]
    print(f'   sketch hints added: median {sorted(m)[len(m)//2] if m else 0}')
