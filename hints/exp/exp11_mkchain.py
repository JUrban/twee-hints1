#!/usr/bin/env python3
"""exp11/mkchain.py IN.cmds OUT.cmds: IN's commands with --hints-file replaced by the goal's chain (sibchain.py,
records /project/hintwork/chain_records.tsv, UL's 10 nearest proven siblings below it, as now). Chains go to
h_chain/<goal>.hints; sizes.tsv gets goal, pool hints, chain hints."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain
C = sibchain.Chains('/project/hintwork/loops/UL', background=False, records='/project/hintwork/chain_records.tsv')
solved = {}
for l in open('/project/hintwork/loops/UL/solved.tsv'):
    g = l.split('\t')[0]
    if '__goal_' in g:
        o, k = g.rsplit('__goal_', 1); solved.setdefault(o, set()).add(int(k))
os.makedirs('h_chain', exist_ok=True)
with open(sys.argv[2], 'w') as f, open('sizes.tsv', 'w') as z:
    for l in open(sys.argv[1]):
        g, cmd = l.rstrip('\n').split('\t'); w = cmd.split()
        p = os.path.abspath(f'h_chain/{g}.hints')
        if not os.path.exists(p):
            hs = C.chain(g, solved.get(g.rsplit('__goal_', 1)[0], set()), 10)
            open(p, 'w').write(''.join(f'{a}\t{b}\n' for a, b in hs))
        i = w.index('--hints-file')
        z.write(f'{g}\t{sum(1 for _ in open(w[i + 1]))}\t{sum(1 for _ in open(p))}\n')
        w[i + 1] = p
        f.write(g + '\t' + ' '.join(w) + '\n')
