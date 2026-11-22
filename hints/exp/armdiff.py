#!/usr/bin/env python3
"""armdiff.py A B [--at MIN] [--root loops]: the goals one arm proved by MIN minutes and the other did not (22 Nov).

A goal is proved by MIN when its hints file's mtime is within MIN minutes of config.json's (as abs/setcurve.py).
For each arm's only-goals: how that arm proved them (synced from transfer/givenmatch, or the level of the proving
run, and whether it was the goal's first run), how many runs the other arm gave them (all rows so far), and for the
ones proved at a first run, when (by row position, turned into minutes with the loop log's cascade lines) each arm
first ran them."""
import os, re, sys, argparse, collections, statistics as st
ap = argparse.ArgumentParser()
ap.add_argument('a'); ap.add_argument('b')
ap.add_argument('--at', type=float, default=240); ap.add_argument('--root', default='loops')
o = ap.parse_args()
T = o.at * 60
def solved_at(z):
    t0 = os.stat(f'{o.root}/{z}/config.json').st_mtime
    with os.scandir(f'{o.root}/{z}/hints') as it:
        return {e.name for e in it if e.stat().st_mtime - t0 <= T}
def rows(z):
    r = collections.defaultdict(list); first = {}; n = 0
    for line in open(f'{o.root}/{z}/r1/results.tsv', errors='replace'):
        w = line.rstrip('\n').split('\t'); n += 1
        if len(w) > 4:
            r[w[0]].append((w[1], w[4])); first.setdefault(w[0], n)
    return r, first
def runs_to_min(z):   # (runs, minute) pairs from the cascade lines
    pts = []
    for line in open(f'{o.root}/{z}.log', errors='replace'):
        m = re.search(r'cascade: (\d+) runs, .*? (\d+)s,', line)
        if m: pts.append((int(m.group(1)), int(m.group(2)) / 60))
    def f(k):
        for r, mi in pts:
            if r >= k: return mi
        return pts[-1][1] if pts else float('nan')
    return f
S = {z: solved_at(z) for z in (o.a, o.b)}
R = {}; F = {}; M = {}
for z in (o.a, o.b):
    R[z], F[z] = rows(z); M[z] = runs_to_min(z)
A, B = S[o.a], S[o.b]
print(f'at {o.at:g} min: {o.a} {len(A)}, {o.b} {len(B)}, {o.a}-only {len(A-B)}, {o.b}-only {len(B-A)}, union {len(A|B)}')
for z, w, only in ((o.a, o.b, A - B), (o.b, o.a, B - A)):
    c = collections.Counter(); nr = collections.Counter(); fr = []
    for g in only:
        rr = R[z].get(g, [])
        i = next((k for k, x in enumerate(rr) if x[0] == 'THM'), None)
        if i is None: c['synced'] += 1; continue
        c[('first ' if i == 0 else 'later ') + re.sub(r'@.*', '', rr[i][1])] += 1
        n = len(R[w].get(g, [])); nr['0' if n == 0 else '1-2' if n <= 2 else '3+'] += 1
        if i == 0 and g in F[w]: fr.append((M[z](F[z][g]), M[w](F[w][g])))
    print(f'{z}-only {len(only)}, by how {z} proved them: ' + ', '.join(f'{k} {v}' for k, v in c.most_common()))
    print(f'   the proved-by-a-run ones had from {w} (rows so far): ' + ', '.join(f'{k} runs {nr[k]}' for k in ('0', '1-2', '3+')))
    if len(fr) >= 4:
        q = lambda xs: '/'.join(f'{v:.0f}' for v in st.quantiles(xs, n=4))
        print(f'   proved at their first run ({len(fr)}): minute of the first run, quartiles: {z} {q([x for x, _ in fr])}, {w} {q([y for _, y in fr])}')
