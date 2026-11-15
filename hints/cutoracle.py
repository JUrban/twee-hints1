#!/usr/bin/env python3
"""Oracle cut candidates for loop.py --gen-cuts (15 Nov): instead of the generator's samples, rules of the
goal's later proof (CUT_ORACLE_DIR/<name>, a hints dir of a run that solved it), so an online test bounds
what cuts can give at a cut budget. CUT_ORACLE=last (the rules nearest the goal), first, or spread (evenly
spaced). Called as the generator: cutoracle.py hints CTX NAME ... --counts 1 (prints l, r, count)."""
import os, sys
name = sys.argv[3]
k = int(os.environ.get('CUT_ORACLE_K', '40'))
mode = os.environ.get('CUT_ORACLE', 'spread')
p = os.path.join(os.environ['CUT_ORACLE_DIR'], name)
rows = [l.rstrip('\n').split('\t')[:2] for l in open(p)] if os.path.exists(p) else []
rows = [r for r in rows if len(r) == 2]
if mode == 'last':
    rows = rows[-k:][::-1]
elif mode == 'first':
    rows = rows[:k]
elif len(rows) > k:
    rows = [rows[round(i * (len(rows) - 1) / (k - 1))] for i in range(k)][::-1]
for l, r in rows:
    print(f'{l}\t{r}\t1')
