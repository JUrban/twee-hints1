#!/usr/bin/env python3
"""exp21/mk.py: the L0 portfolio arms on the 300 goals, all at 5 abstract s (--max-cpu 50), from the captured
5 s commands (B_5.cmds: production's fresh run, 30 kNN lemmas; K60_5.cmds: the same with 60). One command file
A.cmds, ids ARM:goal, goal-major (every arm of a goal before the next goal), so a partial run is balanced.
  C    control: the captured command as it is
  K60  60 kNN lemmas (K60 capture; everything but the problem file must match C)
  U    definitions unfolded (unfold.py, problem and hints, as loop.py --variants unf and exp15)
  S    --eqhint-subsume
  R2   rule-model threshold 0.2 instead of 0.1
  N    no rule model
  G    no parental guidance (--pg-threshold dropped)
  X    chain hints (sibchain.py, chain_records2.tsv, the 10 nearest proven siblings below, as production's 80 s
       level) instead of the pool
Writes A.cmds, p/<goal>.u.p, h/<arm>/<goal>.hints, sizes.tsv (goal, pool hints, chain hints, definitions)."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import sibchain, unfold
def load(p):
    return dict(l.rstrip('\n').split('\t') for l in open(p))
B = load('B_5.cmds'); K = load('K60_5.cmds')
G = [l.strip() for l in open('goals300') if l.strip()]
assert set(B) == set(K) == set(G), (len(B), len(K), len(G))
C = sibchain.Chains('/project/hintwork/loops/UL', background=False, records='/project/hintwork/chain_records2.tsv')
solved = {}
for l in open('cap/B.ctx/solved.tsv'):   # (the capture's context)
    g = l.split('\t')[0]
    if '__goal_' in g:
        o, k = g.rsplit('__goal_', 1); solved.setdefault(o, set()).add(int(k))
for d in ('p', 'h/U', 'h/X'):
    os.makedirs(d, exist_ok=True)
def drop(w, flag, n):   # remove FLAG and its N values
    i = w.index(flag); return w[:i] + w[i + 1 + n:]
with open('A.cmds', 'w') as f, open('sizes.tsv', 'w') as z:
    for g in G:
        w = B[g].split(); wk = K[g].split()
        assert w[0] == '/project/bin/twee-e61' and w[w.index('--max-time') + 1] == '5'
        assert [x for i, x in enumerate(w) if i != 1] == [x for i, x in enumerate(wk) if i != 1], g
        hi = w.index('--hints-file')
        arms = {'C': w, 'K60': wk, 'S': w + ['--eqhint-subsume']}
        r = list(w); i = r.index('--rule-threshold'); assert r[i + 1] == '0.1'; r[i + 1] = '0.2'; arms['R2'] = r
        n = list(w)
        for fl in ('--rule-model', '--rule-vocab', '--rule-goal', '--rule-threshold', '--rule-penalty'):
            n = drop(n, fl, 1)
        arms['N'] = n
        p = list(w); i = p.index('--pg-threshold'); assert p[i + 1] == '0.25'; arms['G'] = drop(p, '--pg-threshold', 1)
        txt, defs = unfold.unfold_text(open(w[1]).read())
        up = os.path.abspath(f'p/{g}.u.p'); open(up, 'w').write(txt)
        hs = [l.rstrip('\n').split('\t') for l in open(w[hi + 1])]
        uh = os.path.abspath(f'h/U/{g}.hints')
        open(uh, 'w').write(''.join('\t'.join([unfold.unfold_eq(x, defs) for x in h[:2]] + h[2:]) + '\n' for h in hs))
        u = list(w); u[1] = up; u[hi + 1] = uh; arms['U'] = u
        ch = C.chain(g, solved.get(g.rsplit('__goal_', 1)[0], set()), 10)
        xh = os.path.abspath(f'h/X/{g}.hints'); open(xh, 'w').write(''.join(f'{a}\t{b}\n' for a, b in ch))
        x = list(w); x[hi + 1] = xh; arms['X'] = x
        z.write(f'{g}\t{len(hs)}\t{len(ch)}\t{len(defs)}\n')
        for a in ('C', 'K60', 'U', 'S', 'R2', 'N', 'G', 'X'):
            f.write(f'{a}:{g}\t' + ' '.join(arms[a]) + '\n')
print(len(G), 'goals, 8 arms')
