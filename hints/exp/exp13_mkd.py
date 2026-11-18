#!/usr/bin/env python3
"""exp13/mkd.py: arm D, exp8's chain commands with only the 10 siblings' own proofs as hints (their hint files in
UL, or the record's loop, nearest first, duplicates dropped): the chain without the expansion. Writes h_D/, D.cmds,
sizesD.tsv (goal, exp8 chain, D)."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain
C = sibchain.Chains('/project/hintwork/loops/UL', background=False, records='/project/hintwork/chain_records.tsv')
sibs = {}
for l in open('/project/hintwork/exp8/sibs10.tsv'):
    g, s = l.rstrip('\n').split('\t')[:2]
    sibs[g] = [x for x in s.split(',') if x]
os.makedirs('h_D', exist_ok=True)
with open('D.cmds', 'w') as f, open('sizesD.tsv', 'w') as z:
    for l in open('/project/hintwork/exp8/stall78_K.cmds'):
        g, cmd = l.rstrip('\n').split('\t'); w = cmd.split()
        seen, hs = set(), []
        for x in sibs[g]:
            for d in (C.where.get(x), '/project/hintwork/loops/UL'):
                if d and os.path.exists(os.path.join(d, 'hints', x)):
                    for line in open(os.path.join(d, 'hints', x)):
                        t = tuple(line.rstrip('\n').split('\t')[:2])
                        if len(t) == 2 and t not in seen:
                            seen.add(t); hs.append(t)
                    break
        p = os.path.abspath(f'h_D/{g}.hints')
        open(p, 'w').write(''.join(f'{a}\t{b}\n' for a, b in hs))
        i = w.index('--hints-file')
        z.write(f'{g}\t{sum(1 for _ in open(w[i + 1]))}\t{len(hs)}\n')
        w[i + 1] = p
        f.write(g + '\t' + ' '.join(w) + '\n')
