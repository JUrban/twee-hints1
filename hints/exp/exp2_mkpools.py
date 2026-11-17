#!/usr/bin/env python3
"""exp2/mkpools.py: for each test goal (goals200, captured in ORD's final context, pg/tb), the hints its
original's ORD pool would gain if every ORD proof's hint file were its expansion (exp2/xd, closure within ORD's
own records, so no proof of a test goal can enter). Extras = hints in the siblings' expansions, not in the
captured hints file, most frequent (over siblings) first. Writes h_xa/<g>.hints (captured + extras at the
default factor) and h_xw/<g>.hints (extras at factor 0.1), and extras.tsv: goal, captured, extras."""
import collections, os
G = open('goals200').read().split()
sibs = collections.defaultdict(list)
for s in open('ord_sibs').read().split():
    sibs[s.rsplit('__goal_', 1)[0]].append(s)
cache = {}
def lines(s):
    if s not in cache:
        try: cache[s] = {tuple(x.split('\t')[:2]) for x in open('xd/' + s).read().splitlines() if '\t' in x}
        except OSError: cache[s] = set()
    return cache[s]
os.makedirs('h_xa', exist_ok=True); os.makedirs('h_xw', exist_ok=True)
with open('extras.tsv', 'w') as t:
    for g in G:
        o = g.rsplit('__goal_', 1)[0]
        base = open(f'/project/hintwork/pg/tb/tmp/{g}.hints').read().splitlines()
        bk = {tuple(x.split('\t')[:2]) for x in base}
        c = collections.Counter()
        for s in sibs[o]:
            c.update(lines(s) - bk)
        ex = [h for h, _ in c.most_common()]
        with open(f'h_xa/{g}.hints', 'w') as f:
            f.write('\n'.join(base + ['\t'.join(h) for h in ex]) + '\n')
        with open(f'h_xw/{g}.hints', 'w') as f:
            f.write('\n'.join(base + ['\t'.join(h) + '\t0.1' for h in ex]) + '\n')
        t.write(f'{g}\t{len(bk)}\t{len(ex)}\n')
