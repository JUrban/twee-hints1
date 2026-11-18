#!/usr/bin/env python3
"""exp21/pick.py: 300 goals for the L0 portfolio test. Unsolved in loops/UL (solved.tsv at pick time) whose last
row in UL r5's results is a failed fresh run (L0 NO): the goals production holds after a 5 s failure. Sampled with
random.Random(21) from the sorted candidates. Writes goals300 and pick.txt (counts)."""
import random
U = {l.split('\t')[0] for l in open('/project/hintwork/loops/UL/solved.tsv')}
last = {}
for l in open('/project/hintwork/loops/UL/r5/results.tsv'):
    w = l.rstrip('\n').split('\t')
    if len(w) >= 5:
        last[w[0]] = (w[1], w[4])
cand = sorted(n for n, (ok, lev) in last.items() if ok == 'NO' and lev == 'L0' and n not in U)
G = sorted(random.Random(21).sample(cand, 300))
open('goals300', 'w').write(''.join(g + '\n' for g in G))
o = {g.rsplit('__goal_', 1)[0] for g in G}
msg = f'{len(U)} solved, {len(last)} goals with r5 rows, {len(cand)} candidates, 300 picked from {len(o)} originals'
open('pick.txt', 'w').write(msg + '\n'); print(msg)
