#!/usr/bin/env python3
"""mkhints.py PROBLEM TWEE_OUTPUT OUT.tsv [--aux]: generalized hint file from a twee --print-hints run."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib as h
name, out, dst = sys.argv[1:4]
t = open(out).read()
L, G = h.extract_hints(t)
A = h.extract_aux(t) if '--aux' in sys.argv else []
sig = h.problem_signature(name)
seen = []
for l, r in L + G + A:
    k = min(h.generalize(l, r, sig), h.generalize(r, l, sig))
    if k[0] != k[1] and k not in seen:
        seen.append(k)
with open(dst, 'w') as f:
    for l, r in seen:
        f.write(f'{l}\t{r}\n')
print(len(L), len(G), len(A), len(seen))
