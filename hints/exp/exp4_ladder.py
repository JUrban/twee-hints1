#!/usr/bin/env python3
"""exp4/ladder.py RUNGS.tsv PROVE.tsv... OUT.tsv: the next rung down. For each rung conjecture (rungs.py rows) not
proved in any PROVE file (sketch.py results; compared up to renaming and orientation), the goal's own screened up
moves (mv/<goal>.tsv rows of kind group, filter or law with screen 'ok') are written again with the conjecture as
target (7th column), so sketch.py, reinst.py and refine.py climb the conjecture as they climbed the goal.
Ids: <rung id>_<move id>."""
import re, sys
*src, dst = sys.argv[1:]
rungs, proves = src[0], src[1:]
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        return re.sub(r'\bX\d+\b', f, x) + ' = ' + re.sub(r'\bX\d+\b', f, y)
    return min(ren(l, r), ren(r, l))
proved = set()
for p in proves:
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        if w[4] == '1': proved.add((w[0], canon(w[3])))
n = 0
with open(dst, 'w') as f:
    for l in open(rungs):
        g, rid, _, c = l.rstrip('\n').split('\t')[:4]
        if (g, canon(c)) in proved: continue
        for m in open(f'mv/{g}.tsv'):
            w = m.rstrip('\n').split('\t')
            if w[2] in ('group', 'filter', 'law') and w[4] == 'ok':
                f.write('\t'.join([g, f'{rid}_{w[1]}', w[2], w[3], 'ok', w[5], c]) + '\n'); n += 1
print(n, 'sketch rows')
