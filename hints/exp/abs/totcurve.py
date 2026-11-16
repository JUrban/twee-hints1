#!/usr/bin/env python3
"""(16 Nov 18:15) Total proved goals of a from-scratch arm over time, cascade and transfer together, from the
mtimes of OUT/hints/* and OUT.xfer/hints/* (first proof of each goal of SET), in minutes since OUT/config.json.
usage: totcurve.py SET ARM [ARM ...]"""
import os, sys
S = {l.strip() for l in open(sys.argv[1]) if l.strip()}
for a in sys.argv[2:]:
    t0 = os.path.getmtime(f'loops/{a}/config.json')
    first = {}
    for d in (f'loops/{a}/hints', f'loops/{a}.xfer/hints'):
        if os.path.isdir(d):
            for n in os.listdir(d):
                if n in S:
                    t = (os.path.getmtime(os.path.join(d, n)) - t0) / 60
                    first[n] = min(first.get(n, 1e9), t)
    ts = sorted(first.values())
    print(a, ' '.join(f'{m}:{sum(t <= m for t in ts)}' for m in (1, 4, 10, 15, 25, 40, 60)), 'all', len(ts))
