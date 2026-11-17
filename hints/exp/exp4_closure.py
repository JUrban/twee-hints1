#!/usr/bin/env python3
"""exp4/closure.py REFINE.tsv PROVE.tsv...: which goals are solved through a rung.
A refinement proof (refine.py row with proved = 1) proves its goal from the conjectures in its column 7. The goal
is solved when every one of them is proved as a goal in T (sketch.py rows of rungs.py's conjectures, column 5 = 1;
conjectures compared up to renaming and orientation). Prints per goal: solved or not, the best proof (fewest
unproved conjectures), and the conjectures still open."""
import collections, re, sys
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        return re.sub(r'\bX\d+\b', f, x) + ' = ' + re.sub(r'\bX\d+\b', f, y)
    return min(ren(l, r), ren(r, l))
proved, tried = collections.defaultdict(set), collections.defaultdict(set)
for p in sys.argv[2:]:
    for l in open(p):
        w = l.rstrip('\n').split('\t'); k = canon(w[3]); tried[w[0]].add(k)
        if w[4] == '1': proved[w[0]].add(k)
best = {}
for l in open(sys.argv[1]):
    w = l.rstrip('\n').split('\t')
    if w[3] != '1' or not w[6]: continue
    cs = w[6].split('; '); open_ = [c for c in cs if canon(c) not in proved[w[0]]]
    if w[0] not in best or len(open_) < len(best[w[0]][1]): best[w[0]] = (w[1], open_, len(cs))
solved = [g for g, b in best.items() if not b[1]]
print(f'{len(best)} goals with a rung proof, {len(solved)} solved through one')
for g in sorted(best):
    src, open_, n = best[g]
    st = 'SOLVED' if not open_ else f'{len(open_)} of {n} open (tried {sum(canon(c) in tried[g] for c in open_)})'
    print(f'  {g}: refine {src}, {st}')
