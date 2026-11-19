#!/usr/bin/env python3
"""exp37: paired comparison of the replay arms (loops/MQ_<model>_20) against the control MQ_rm4t_20, and the
union and unique proofs per CPU hour. mqcmp.py [MODELS...]"""
import glob, os, sys

def load(d):
    r = {}
    p = f'/project/hintwork/loops/{d}/results.tsv'
    if os.path.exists(p):
        for l in open(p):
            w = l.split('\t')
            r[w[0]] = (w[1] == 'THM', float(w[2]))
    return r

ms = sys.argv[1:] or sorted(os.path.basename(d)[3:-3] for d in glob.glob('/project/hintwork/loops/MQ_*_20'))
R = {m: load(f'MQ_{m}_20') for m in ms}
c = R.get('rm4t', {})
common = set.intersection(*(set(r) for r in R.values())) if R else set()
print(f'{len(common)} goals run by every arm')
for m, a in R.items():
    g = [x for x in a if x in c]
    pa = {x for x in g if a[x][0]}; pc = {x for x in g if c[x][0]}
    cpu = sum(a[x][1] for x in g) / 3600
    others = set().union(*({x for x in common if R[o][x][0]} for o in R if o != m)) if len(R) > 1 else set()
    uniq = {x for x in common if a[x][0]} - others
    print(f'{m:6} rows {len(a):3}  vs control on {len(g):3}: {len(pa):3} / {len(pc):3}  +{len(pa - pc)} -{len(pc - pa)}  '
          f'CPU {cpu:.2f} h  unique among all arms {len(uniq)} {sorted(uniq)[:3]}')
if common:
    print('union over every arm on the common goals:', len({x for x in common for r in R.values() if r[x][0]}),
          ' control alone:', sum(c[x][0] for x in common) if c else '-')
