"""heads.py TRUSTED [--set sets/all] [--local]: the heads of the unsolved goals, one per original that has any: its first
unsolved goal by goal number (so every earlier sibling is proved). Prints one goal per line, in --set order.
(23 Nov, notes/2026-11-23-plain-sizes.md "The frontier is 92 heads": the other unsolved goals sit behind these.)
--local (24 Nov, exp72): every unsolved goal whose previous goal of its original (by goal number, in --set) is proved,
the first heads included (sets/localheads71 is this list without the first heads, 23 Nov 23:33)."""
import collections, sys
a = sys.argv[1:]
SET = a[a.index('--set') + 1] if '--set' in a else '/project/hintwork/sets/all'
T = {l.split()[0] for l in open(a[0]) if l.strip()}
G = [l.strip() for l in open(SET) if l.strip()]
if '--local' in a:
    by = collections.defaultdict(list)
    for g in G:
        o, k = g.rsplit('__goal_', 1)
        by[o].append((int(k), g))
    H = set()
    for v in by.values():
        v.sort()
        H |= {g for i, (k, g) in enumerate(v) if g not in T and (i == 0 or v[i - 1][1] in T)}
else:
    first = {}
    for g in G:
        if g in T:
            continue
        o, k = g.rsplit('__goal_', 1)
        if o not in first or int(k) < first[o][0]:
            first[o] = (int(k), g)
    H = {g for _, g in first.values()}
for g in G:
    if g in H:
        print(g)
