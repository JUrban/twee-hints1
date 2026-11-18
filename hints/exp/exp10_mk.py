#!/usr/bin/env python3
"""exp10/mk.py: exp8's chain commands (stall78_K.cmds) with chains from sibchain.py over a records file, for exp8's
own siblings (sibs10.tsv, picked 07:11). Writes h_X/<goal>.hints, X.cmds and sizes.tsv (goal, exp8 chain, chain
without transfer records, chain with them).
  python3 mk.py RECORDS_WITH_TRANSFER RECORDS_WITHOUT"""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain
X = sibchain.Chains('/project/hintwork/loops/UL', background=False, records=sys.argv[1])
B = sibchain.Chains('/project/hintwork/loops/UL', background=False, records=sys.argv[2])
sibs = {}
for l in open('/project/hintwork/exp8/sibs10.tsv'):
    g, s = l.rstrip('\n').split('\t')[:2]
    sibs[g] = {int(x.rsplit('__goal_', 1)[1]) for x in s.split(',') if x}
with open('X.cmds', 'w') as f, open('sizes.tsv', 'w') as z:
    for l in open('/project/hintwork/exp8/stall78_K.cmds'):
        g, cmd = l.rstrip('\n').split('\t'); w = cmd.split()
        hx = X.chain(g, sibs[g], 10); hb = B.chain(g, sibs[g], 10)
        p = os.path.abspath(f'h_X/{g}.hints')
        open(p, 'w').write(''.join(f'{a}\t{b}\n' for a, b in hx))
        old = w[w.index('--hints-file') + 1]
        z.write(f'{g}\t{sum(1 for _ in open(old))}\t{len(hb)}\t{len(hx)}\n')
        w[w.index('--hints-file') + 1] = p
        f.write(g + '\t' + ' '.join(w) + '\n')
