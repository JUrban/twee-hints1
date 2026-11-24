#!/usr/bin/env python3
"""clqread.py CLS71_LOG_LINE CLS71_TSV_ROW: exp83 reading (notes/2026-11-24-quick-finals.md). CLQ83 (its climb.tsv after the 3 rows
of its first start) against CLS71 from that log line and climb.tsv row on (15:36: 1570, 20123): finished, proved, CPU h
(climb.tsv seconds of finished targets), proofs per CPU h."""
import re, sys
H = '/project/hintwork'
def rd(log, tsv, from_line, skip_rows):
    L = open(log).read().splitlines()[from_line - 1:]
    done = {m.group(1): m.group(2) == 'THM' for l in L for m in [re.match(r'(\S+__goal_\d+) (THM|NO) ', l)] if m}
    rows = open(tsv).read().splitlines()[skip_rows:]
    cpu = 0.0
    for l in rows:
        w = l.split('\t')
        if w[0] in done:
            try: cpu += float(w[5])
            except (ValueError, IndexError): pass
    p = sum(done.values())
    return len(done), p, cpu / 3600
a = rd(f'{H}/loops/CLQ83.log', f'{H}/loops/CLQ83/climb.tsv', 1, 3)
b = rd(f'{H}/loops/CLS71.log', f'{H}/loops/CLS71/climb.tsv', int(sys.argv[1]), int(sys.argv[2]))
for n, (f, p, c) in (('CLQ83', a), ('CLS71', b)):
    print(f'{n}: finished {f} proved {p} CPU h {c:.2f} per CPU h {p / c if c else 0:.2f}')
