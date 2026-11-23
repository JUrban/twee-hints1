"""heads.py TRUSTED [--set sets/all]: the heads of the unsolved goals, one per original that has any: its first
unsolved goal by goal number (so every earlier sibling is proved). Prints one goal per line, in --set order.
(23 Nov, notes/2026-11-23-plain-sizes.md "The frontier is 92 heads": the other unsolved goals sit behind these.)"""
import sys
a = sys.argv[1:]
SET = a[a.index('--set') + 1] if '--set' in a else '/project/hintwork/sets/all'
T = {l.split()[0] for l in open(a[0]) if l.strip()}
first = {}
G = [l.strip() for l in open(SET) if l.strip()]
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
