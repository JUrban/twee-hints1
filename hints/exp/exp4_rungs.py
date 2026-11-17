#!/usr/bin/env python3
"""exp4/rungs.py REFINE.tsv OUT.tsv: the conjectures that refinement runs used to prove their goal (refine.py
column 7), one row each in moves.py format, kind 'gen' (sketch.py runs them as goals), deduplicated per goal up to
renaming and orientation. Detail column: the refine rows (source ids) whose proofs used it, and how many
conjectures each of those proofs used (a goal is solved when every conjecture of one proof is proved).
Ids start at 4000."""
import collections, re, sys
src, dst = sys.argv[1:]
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        return re.sub(r'\bX\d+\b', f, x) + ' = ' + re.sub(r'\bX\d+\b', f, y)
    return min(ren(l, r), ren(r, l))
per = collections.defaultdict(dict)
for l in open(src):
    w = l.rstrip('\n').split('\t')
    if w[3] != '1' or not w[6]: continue
    cs = w[6].split('; ')
    for c in cs:
        k = canon(c); per[w[0]].setdefault(k, [c, []])[1].append(f'{w[1]}/{len(cs)}')
with open(dst, 'w') as f:
    for g in sorted(per):
        for i, (c, srcs) in enumerate(per[g].values()):
            f.write(f'{g}\t{4000 + i}\tgen\t{c}\tok\tused by {" ".join(srcs)}\n')
