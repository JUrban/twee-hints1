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

# (20 Nov) Greedy cover (Mizar60's model portfolio) over the arms that ran every goal of the common set: the arm with
# most proofs first, then each next arm by the proofs it adds, with each arm's CPU on the common goals.
if common and len(R) > 1:
    left = dict(R); got = set(); order = []
    while left:
        m = max(left, key=lambda k: (len({x for x in common if left[k][x][0]} - got), -sum(left[k][x][1] for x in common)))
        add = {x for x in common if left[m][x][0]} - got
        order.append((m, len(add), sum(left[m][x][1] for x in common) / 3600)); got |= add; del left[m]
    print('greedy cover on the common goals:', ', '.join(f'{m} +{k} ({c:.2f} CPU h)' for m, k, c in order),
          f'-> {len(got)}')
