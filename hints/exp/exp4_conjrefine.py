#!/usr/bin/env python3
"""exp4/conjrefine.py CONJ.tsv OUT.tsv [-j J] [--time T] [--secs S]: the sufficiency step for conj.py's
model-based conjectures.
1. Each conjecture is screened again with Mace4 in T (sizes 2..12, S seconds, default 30): conj.py only checked
   it in the models it had collected.
2. Per goal, the survivors are given together as assumptions (fof(assume_i, axiom, ...)) to the goal's production
   command at T abstract s (default 20), exactly as refine.py does (its run()).
If the goal proves, the assumptions its proof used (USEDAXIOMS) are rungs: conjectures that suffice for the goal.
OUT.tsv: refine.py's format (goal, 'conj', given, proved, used, CPU s, the used conjectures); rungs.py reads it.
Screen results in OUT.screen.tsv (goal, conjecture, countermodel size or '-')."""
import argparse, collections, concurrent.futures as cf, os, sys
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
from moves import ladr, mace
ns = {}
src = open(f'{here}/refine.py').read()
exec(src[:src.index('ap = argparse')], ns)   # TB, cmds, run(g, src, conj, T, out_dir)
ap = argparse.ArgumentParser(); ap.add_argument('conj'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=2); ap.add_argument('--time', type=float, default=20)
ap.add_argument('--secs', type=int, default=30)
a = ap.parse_args()
per = collections.defaultdict(list)
for l in open(a.conj):
    w = l.rstrip('\n').split('\t'); per[w[0]].append(w[2])
pairs = [(g, c) for g in per for c in per[g]]
def scr(p):
    A, _ = ladr(p[0]); return p, mace(A, p[1], a.secs, end=12)
keep = collections.defaultdict(list)
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out + '.screen.tsv', 'w') as f:
    for (g, c), n in ex.map(scr, pairs):
        f.write(f'{g}\t{c}\t{n if n else "-"}\n'); f.flush()
        if not n: keep[g].append(c)
jobs = [(g, 'conj', keep[g]) for g in sorted(keep) if keep[g]]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for res in ex.map(lambda x: ns['run'](*x, a.time, a.out + '.d'), jobs):
        f.write('\t'.join(map(str, res)) + '\n'); f.flush()
