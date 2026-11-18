#!/usr/bin/env python3
"""exp13/mk.py N: exp8's chain commands (stall78_K.cmds) with the chain of only the N nearest of exp8's siblings
(sibs10.tsv, picked 07:11, nearest first), records chain_records.tsv. Writes h_S<N>/<goal>.hints, S<N>.cmds and
sizes<N>.tsv (goal, exp8 chain, chain of N)."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain
N = int(sys.argv[1])
C = sibchain.Chains('/project/hintwork/loops/UL', background=False, records='/project/hintwork/chain_records.tsv')
sibs = {}
for l in open('/project/hintwork/exp8/sibs10.tsv'):
    g, s = l.rstrip('\n').split('\t')[:2]
    sibs[g] = {int(x.rsplit('__goal_', 1)[1]) for x in s.split(',') if x}
os.makedirs(f'h_S{N}', exist_ok=True)
with open(f'S{N}.cmds', 'w') as f, open(f'sizes{N}.tsv', 'w') as z:
    for l in open('/project/hintwork/exp8/stall78_K.cmds'):
        g, cmd = l.rstrip('\n').split('\t'); w = cmd.split()
        hs = C.chain(g, sibs[g], N)
        p = os.path.abspath(f'h_S{N}/{g}.hints')
        open(p, 'w').write(''.join(f'{a}\t{b}\n' for a, b in hs))
        i = w.index('--hints-file')
        z.write(f'{g}\t{sum(1 for _ in open(w[i + 1]))}\t{len(hs)}\n')
        w[i + 1] = p
        f.write(g + '\t' + ' '.join(w) + '\n')
