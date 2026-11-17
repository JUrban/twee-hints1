#!/usr/bin/env python3
"""mkpool.py NAMES LOOP OUTDIR: for each goal, the loop's pool for its original as loop.py --pool original
builds it (every solved goal's hint file, most frequent first), the goal's own steps included."""
import collections, os, sys
names, loop, out = sys.argv[1:]
G = [l.strip() for l in open(names) if l.strip()]
O = {g.rsplit('__goal_', 1)[0] for g in G}
cnt = {o: collections.Counter() for o in O}
for l in open(os.path.join(loop, 'solved.tsv')):
    n = l.split('\t')[0]; o = n.rsplit('__goal_', 1)[0]
    if o not in cnt: continue
    try: lines = open(os.path.join(loop, 'hints', n)).read().splitlines()
    except OSError: continue
    for x in set(tuple(y.split('\t')[:2]) for y in lines if '\t' in y):
        cnt[o][x] += 1
os.makedirs(out, exist_ok=True)
for g in G:
    with open(os.path.join(out, g), 'w') as f:
        for (l, r), _ in cnt[g.rsplit('__goal_', 1)[0]].most_common():
            f.write(f'{l}\t{r}\n')
print({o: len(c) for o, c in sorted(cnt.items(), key=lambda x: -len(x[1]))[:5]}, len(O), 'originals')
