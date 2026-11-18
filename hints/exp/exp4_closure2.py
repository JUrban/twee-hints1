#!/usr/bin/env python3
"""exp4/closure2.py REFINE.tsv --ladder LREFINE.tsv... --proved PROVE.tsv...: closure over the ladder.
A conjecture is proved if a PROVE file proves it as a goal, or if some ladder refinement proof (LREFINE rows:
column 8 = the target conjecture) of it used only proved conjectures (other than itself); repeated to a fixpoint.
A goal is solved if some REFINE proof of it used only proved conjectures. Prints the solved goals and their
chains."""
import argparse, collections, re
ap = argparse.ArgumentParser(); ap.add_argument('refine'); ap.add_argument('--ladder', nargs='*', default=[])
ap.add_argument('--proved', nargs='+'); a = ap.parse_args()
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        return re.sub(r'\bX\d+\b', f, x) + ' = ' + re.sub(r'\bX\d+\b', f, y)
    return min(ren(l, r), ren(r, l))
why = {}
for p in a.proved:
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        if w[4] == '1': why.setdefault((w[0], canon(w[3])), f'proved in {p} id {w[1]}')
lad = []
for p in a.ladder:
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        if w[3] == '1' and w[6] and len(w) > 7:
            t = canon(w[7]); us = [canon(c) for c in w[6].split('; ')]
            if t not in us: lad.append((w[0], t, us, f'{p} {w[1]}'))
changed = True
while changed:
    changed = False
    for g, t, us, src in lad:
        if (g, t) not in why and all((g, u) in why for u in us):
            why[(g, t)] = f'from {len(us)} by {src}'; changed = True
solved = {}
goals = set()
for l in open(a.refine):
    w = l.rstrip('\n').split('\t')
    if w[3] != '1' or not w[6]: continue
    goals.add(w[0]); us = [canon(c) for c in w[6].split('; ')]
    if w[0] not in solved and all((w[0], u) in why for u in us): solved[w[0]] = (w[1], us)
print(f'{len(goals)} goals with a rung proof, {len(solved)} solved')
for g, (src, us) in sorted(solved.items()):
    print(f'  {g}: refine {src}; ' + '; '.join(f'[{u[:60]}] {why[(g, u)]}' for u in us))
