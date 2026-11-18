#!/usr/bin/env python3
"""exp14/mk.py: exp11's stage-1 commands (s1.cmds: the 107 walls at 80 s, captured 10:38) with the two-sided
chain: the 10 nearest proven siblings by goal-number distance, above or below (ties below first), from UL's
solved.tsv at 10:29 (its first 45,414 rows, the state exp11's walls were computed from), records
chain_records.tsv. Below each wall every sibling was proven then, so exp11's below-only chain differs only in
the siblings above. Writes h_T/<goal>.hints, T.cmds, sizes.tsv (goal, exp11 chain, two-sided chain, siblings
above among the 10)."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain
C = sibchain.Chains('/project/hintwork/loops/UL', background=False, records='/project/hintwork/chain_records.tsv')
solved = {}
for i, l in enumerate(open('/project/hintwork/loops/UL/solved.tsv')):
    if i >= 45414:
        break
    g = l.split('\t')[0]
    if '__goal_' in g:
        o, k = g.rsplit('__goal_', 1); solved.setdefault(o, set()).add(int(k))
os.makedirs('h_T', exist_ok=True)
with open('T.cmds', 'w') as f, open('sizes.tsv', 'w') as z:
    for l in open('/project/hintwork/exp11/s1.cmds'):
        g, cmd = l.rstrip('\n').split('\t'); w = cmd.split()
        o, k = g.rsplit('__goal_', 1); k = int(k); s = solved.get(o, set())
        hs = C.chain(g, s, 10, two_sided=True)
        up = sum(1 for j in sorted((j for j in s if j != k), key=lambda j: (abs(j - k), j > k))[:10] if j > k)
        p = os.path.abspath(f'h_T/{g}.hints')
        open(p, 'w').write(''.join(f'{a}\t{b}\n' for a, b in hs))
        i = w.index('--hints-file')
        z.write(f'{g}\t{sum(1 for _ in open(w[i + 1]))}\t{len(hs)}\t{up}\n')
        w[i + 1] = p
        f.write(g + '\t' + ' '.join(w) + '\n')
