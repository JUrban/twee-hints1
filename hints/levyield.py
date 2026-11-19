#!/usr/bin/env python3
"""levyield.py RESULTS [FROM_ROW]: runs, proofs, CPU hours and proofs per CPU hour of each cascade level label
(L<k>, and V<name> for loop.py --variants) in a loop's results.tsv, from row FROM_ROW (1-based, default 1) on.
(18 Nov, the portfolio task: production ul47 from row 56125.)"""
import collections, sys
f, r0 = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1
n, s, c = collections.Counter(), collections.Counter(), collections.Counter()
for i, l in enumerate(open(f), 1):
    w = l.rstrip('\n').split('\t')
    if i < r0 or len(w) < 5:
        continue
    k = w[4] + ('f' if len(w) >= 8 and w[7] == 'f=1' else '')   # (19 Nov: loop.py --far-deep rows, L1f)
    n[k] += 1; s[k] += w[1] == 'THM'; c[k] += float(w[2])
for k in sorted(n, key=lambda k: (k[0], k)):
    print(f'{k:6} runs {n[k]:6}  proofs {s[k]:4}  CPU h {c[k] / 3600:6.2f}  per CPU h {s[k] / max(c[k] / 3600, 1e-9):6.2f}')
