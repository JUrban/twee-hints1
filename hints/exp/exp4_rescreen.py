#!/usr/bin/env python3
"""exp4/rescreen.py SKETCH.tsv OUT.tsv [-j J] [--secs S] [--end N]: the used instances of S that sketch.py's
screen kept (no countermodel up to size 8 in 5 s) screened again with Mace4 in the real theory T, sizes 2..N
(default 12), S seconds (default 30). The 5 s screen was mostly a timeout: k(A,B) = e in R1dist_to_aa1 has a
countermodel of size 8, found in 11 s. OUT.tsv: goal, instance, countermodel size or '-', seconds."""
import argparse, concurrent.futures as cf, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moves import ladr, mace
ap = argparse.ArgumentParser(); ap.add_argument('sketch'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=3); ap.add_argument('--secs', type=int, default=30)
ap.add_argument('--end', type=int, default=12); a = ap.parse_args()
pairs = []
for l in open(a.sketch):
    r = l.rstrip('\n').split('\t')
    if len(r) < 11 or r[2] == 'inst' or r[4] != '1' or r[5] != '1': continue
    for x in r[10].split('; '):
        if x and not x.startswith('x ') and (r[0], x) not in pairs: pairs.append((r[0], x))
done = {tuple(l.split('\t')[:2]) for l in open(a.out)} if os.path.exists(a.out) else set()
pairs = [p for p in pairs if p not in done]
def one(p):
    t = time.time(); A, _ = ladr(p[0]); n = mace(A, p[1], a.secs, end=a.end)
    return [p[0], p[1], n if n else '-', f'{time.time() - t:.1f}']
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for res in ex.map(one, pairs):
        f.write('\t'.join(map(str, res)) + '\n'); f.flush()
