#!/usr/bin/env python3
"""exp15/mk.py: exp11's stage-1 commands (s1.cmds: the 107 walls at 80 s, captured 10:38, below-only chain
h_chain/) with every definition unfolded (unfold.py, as loop.py --unfold): the problem through
unfold.unfold_text, the chain hints through unfold.unfold_eq with the problem's definitions. Nothing else
changes. Order: the 92 walls exp11 did not prove first (res_s1.tsv), then its 15, each group in s1.cmds order.
Writes p/<goal>.u.p, h_U/<goal>.hints, U.cmds, sizes.tsv (goal, definitions unfolded, hints, chars of the folded
and the unfolded problem)."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import unfold
E = '/project/hintwork/exp11'
proved = {l.split('\t')[0] for l in open(f'{E}/res_s1.tsv') if l.split('\t')[1] == '1'}
os.makedirs('p', exist_ok=True); os.makedirs('h_U', exist_ok=True)
rows = [l.rstrip('\n').split('\t') for l in open(f'{E}/s1.cmds')]
rows = [r for r in rows if r[0] not in proved] + [r for r in rows if r[0] in proved]
with open('U.cmds', 'w') as f, open('sizes.tsv', 'w') as z:
    for g, cmd in rows:
        w = cmd.split()
        src = open(w[1]).read()
        txt, defs = unfold.unfold_text(src)
        pp = os.path.abspath(f'p/{g}.u.p'); open(pp, 'w').write(txt)
        i = w.index('--hints-file'); hs = []
        for l in open(w[i + 1]):
            h = l.rstrip('\n').split('\t')
            hs.append('\t'.join([unfold.unfold_eq(x, defs) for x in h[:2]] + h[2:]))
        hp = os.path.abspath(f'h_U/{g}.hints'); open(hp, 'w').write(''.join(x + '\n' for x in hs))
        w[1] = pp; w[i + 1] = hp
        z.write(f'{g}\t{len(defs)}\t{len(hs)}\t{len(src)}\t{len(txt)}\n')
        f.write(g + '\t' + ' '.join(w) + '\n')
