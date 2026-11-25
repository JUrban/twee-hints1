#!/usr/bin/env python3
"""exp84_read.py: exp84's reading (notes/2026-11-25-precedences.md). Per arm P84O0-P84O4 (loops/P84Ok.log, climb.tsv):
finished, proved, CPU h, proofs per CPU h; the union of the ordering arms O1-O4, the targets only they prove (not
O0), and the targets each arm proves alone."""
import re
H = '/project/hintwork'
T = [l.strip() for l in open(f'{H}/sets/exp84.targets') if l.strip()]
res, cpu = {}, {}
for k in range(5):
    A = f'P84O{k}'
    res[k] = {m.group(1): m.group(2) == 'THM' for l in open(f'{H}/loops/{A}.log')
              for m in [re.match(r'(\S+__goal_\d+) (THM|NO) ', l)] if m}
    s = 0.0
    for l in open(f'{H}/loops/{A}/climb.tsv'):
        w = l.split('\t')
        try:
            s += float(w[5])
        except (ValueError, IndexError):
            pass
    cpu[k] = s / 3600
    p = sum(res[k].values())
    print(f'{A}: finished {len(res[k])}/{len(T)} proved {p} CPU h {cpu[k]:.2f} per CPU h {p / cpu[k] if cpu[k] else 0:.2f}')
pr = {k: {g for g, ok in res[k].items() if ok} for k in res}
U = set().union(*(pr[k] for k in range(1, 5)))
c = sum(cpu[k] for k in range(1, 5))
print(f'orderings O1-O4: union {len(U)}, not proved by O0 {len(U - pr[0])} ({len(U - pr[0]) / c if c else 0:.2f} per CPU h of their {c:.2f}),'
      f' O0 only {len(pr[0] - U)}')
for k in range(5):
    print(f'  P84O{k} alone: {sorted(pr[k] - set().union(*(pr[j] for j in range(5) if j != k)))}')
