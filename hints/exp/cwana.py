#!/usr/bin/env python3
"""(22 Nov 12:08) exp57 (notes/2026-11-22-cp-weights.md): twee's critical-pair weights as members.

  cwana.py [--root /project/hintwork/loops] CONTROL TIMED ARM...

Per arm: goals run and proved, CPU hours (column 3 of its rows), and against CONTROL (CW0): +/-, the union with it and
that union against TIMED (CW9, the control at twice the budget, time-matched for "control + one arm"). Then the union
of all arms, and the goals only one arm proved. Only goals every listed arm has run count, so a partial read compares
like with like. Counts come from the rows.
"""
import collections, os, sys

a = sys.argv[1:]
root = a[a.index('--root') + 1] if '--root' in a else '/project/hintwork/loops'
a = [x for i, x in enumerate(a) if x != '--root' and (i == 0 or a[i - 1] != '--root')]
arms = a
rows = {}
for arm in arms:
    p = os.path.join(root, arm, 'r1', 'results.tsv')
    d = {}
    for l in open(p) if os.path.exists(p) else ():
        w = l.rstrip('\n').split('\t')
        if len(w) >= 3:
            try:
                d[w[0]] = (w[1] == 'THM', float(w[2]))
            except ValueError:
                pass
    rows[arm] = d
common = set.intersection(*(set(d) for d in rows.values())) if rows else set()
ctl, tim = arms[0], arms[1]
P = {arm: {g for g in common if rows[arm][g][0]} for arm in arms}
C = {arm: sum(rows[arm][g][1] for g in common) / 3600 for arm in arms}
print(f'{len(common)} goals run by every arm ({", ".join(f"{x} {len(rows[x])}" for x in arms)} rows)')
print(f'{"arm":5} {"proved":>6} {"CPU h":>6} {"/CPU h":>7} | {"+":>3} {"-":>3} vs {ctl} | union w/ {ctl} | vs {tim} ({len(P[tim])}, {C[tim]:.2f} h)')
for arm in arms:
    pl, mi = len(P[arm] - P[ctl]), len(P[ctl] - P[arm])
    u = P[arm] | P[ctl]
    extra = ''
    if arm not in (ctl, tim):
        extra = f'{len(u):>4} in {C[arm] + C[ctl]:.2f} h | {len(u) - len(P[tim]):+d} ({len(u - P[tim])} not in {tim})'
    print(f'{arm:5} {len(P[arm]):>6} {C[arm]:>6.2f} {len(P[arm]) / max(C[arm], 1e-9):>7.2f} | {pl:>3} {mi:>3}    | {extra}')
allu = set().union(*P.values())
only = collections.Counter()
for g in allu:
    who = [x for x in arms if g in P[x]]
    if len(who) == 1:
        only[who[0]] += 1
print(f'union of all arms: {len(allu)} in {sum(C.values()):.2f} CPU h; only one arm: {dict(only)}')
