#!/usr/bin/env python3
"""exp20/ana.py: the 160 s control against exp11's 80 s runs on the same failed walls. New proofs at 160 s; the
cost of extending (as production would, resuming the 80 s state) = CPU at 160 s minus exp11's CPU at 80 s per goal;
also the full fresh cost. Then each 80 s variant's new proofs on the same goals, at its own full cost."""
def load(p, thm=False):
    d = {}
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        d[w[0]] = ((w[1] == 'THM') if thm else (w[1] == '1'), float(w[2]))
    return d
C80 = load('/project/hintwork/exp11/res_s1.tsv'); C160 = load('res_C160.tsv')
G = sorted(C160)
new = [g for g in G if C160[g][0]]
inc = sum(max(0.0, C160[g][1] - C80[g][1]) for g in G) / 3600
full = sum(C160[g][1] for g in G) / 3600
print(f'{len(G)} failed walls run at 160 s: {len(new)} new; increment {inc:.2f} CPU h ({len(new)/max(inc,1e-9):.2f} per CPU h), '
      f'full {full:.2f} CPU h ({len(new)/max(full,1e-9):.2f} per CPU h)')
print('  new:', new)
for name, p, t in [('K60 exp17', '/project/hintwork/exp17/res_K60.tsv', 0), ('two exp14', '/project/hintwork/exp14/res_T.tsv', 0),
                   ('unf exp15', '/project/hintwork/exp15/res_U.tsv', 0), ('sub exp18', '/project/hintwork/exp18/res_SU.tsv', 0),
                   ('P9+chain exp16', '/project/hintwork/exp16/out_Q/results.tsv', 1), ('sj exp19', '/project/hintwork/exp19/res_SJ.tsv', 0),
                   ('G80 exp22', '/project/hintwork/exp22/res_G80.tsv', 0), ('N80 exp22', '/project/hintwork/exp22/res_N80.tsv', 0)]:
    try:
        R = load(p, t)
    except OSError:
        continue
    H = [g for g in G if g in R]
    if not H:
        continue
    nv = [g for g in H if R[g][0]]; c = sum(R[g][1] for g in H) / 3600
    both = len(set(nv) & set(new))
    print(f'{name:15} on {len(H):3}: {len(nv)} new ({both} also at 160 s), {c:.2f} CPU h, {len(nv)/max(c,1e-9):.2f} per CPU h; '
          f'160 s on these: {sum(1 for g in H if g in new)}')
