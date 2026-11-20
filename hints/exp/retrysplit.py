#!/usr/bin/env python3
"""(20 Nov 18:45) A loop's runs by half hour: first runs against retries (proofs / runs) (notes/2026-11-20-z6.md).
  retrysplit.py DIR [--win 1800]"""
import collections, glob, re, sys
d = sys.argv[1]
win = int(sys.argv[sys.argv.index('--win') + 1]) if '--win' in sys.argv else 1800
runs = []
for p in glob.glob(f'{d}/r*/results.tsv'):
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        m = re.search(r'\bt=(\d+)', l)
        if m and len(w) >= 5:
            runs.append((int(m.group(1)), w[0], w[1]))
W, seen = collections.Counter(), set()
for t, g, st in sorted(runs):
    k = 'first' if g not in seen else 'retry'
    seen.add(g)
    W[(t // win, k, st == 'THM')] += 1
for h in sorted({k[0] for k in W}):
    f1, f0, r1, r0 = W[(h, 'first', True)], W[(h, 'first', False)], W[(h, 'retry', True)], W[(h, 'retry', False)]
    print(f'{h * win // 60:>4} min: first runs {f1}/{f1 + f0}; retries {r1}/{r1 + r0}')
