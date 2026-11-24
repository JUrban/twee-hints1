#!/usr/bin/env python3
"""clq83b_read.py [LOG_LINE] [TSV_ROW]: exp83b's reading (notes/2026-11-24-quick-finals.md, "exp83b"). CLQ83's targets finished
from its log line LOG_LINE+1 (default 1354: the 23:49 restart onto the local heads) and their climb.tsv seconds from row
TSV_ROW+1 on (default 1354): finished, proved, how many are local heads (sets/localheads71), CPU h, proofs per CPU h."""
import re, sys
H = '/project/hintwork'
a = [int(x) for x in sys.argv[1:3]] + [1354, 1354][len(sys.argv[1:3]):]
L = open(f'{H}/loops/CLQ83.log').read().splitlines()[a[0]:]
done = {m.group(1): m.group(2) == 'THM' for l in L for m in [re.match(r'(\S+__goal_\d+) (THM|NO) ', l)] if m}
lh = {l.strip() for l in open(f'{H}/sets/localheads71') if l.strip()}
cpu = 0.0
for l in open(f'{H}/loops/CLQ83/climb.tsv').read().splitlines()[a[1]:]:
    w = l.split('\t')
    if w[0] in done:
        try:
            cpu += float(w[5])
        except (ValueError, IndexError):
            pass
p = sum(done.values())
print(f'exp83b: finished {len(done)} (local heads {len(set(done) & lh)}), proved {p} (local heads '
      f'{sum(v for g, v in done.items() if g in lh)}), CPU h {cpu / 3600:.2f}, per CPU h {p / (cpu / 3600) if cpu else 0:.2f}')
