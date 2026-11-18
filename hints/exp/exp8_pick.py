#!/usr/bin/env python3
"""exp8/pick.py GOALS: the 10 nearest UL-proven siblings below each goal (as exp3_pick.py) -> sibs10.tsv, sibs10."""
import collections, sys
ul = {l.split('\t')[0] for l in open('/project/hintwork/loops/UL/solved.tsv')}
by = collections.defaultdict(list)
for g in sorted({l.strip() for l in open('/project/hintwork/sets/all') if l.strip()}):
    o, k = g.rsplit('__goal_', 1); by[o].append(int(k))
out = open('sibs10.tsv', 'w'); names = set()
for g in open(sys.argv[1]).read().split():
    o, k = g.rsplit('__goal_', 1); k = int(k)
    s = [f'{o}__goal_{j}' for j in sorted((j for j in by[o] if j < k and f'{o}__goal_{j}' in ul), reverse=True)[:10]]
    names |= set(s); out.write(f'{g}\t' + ','.join(s) + '\n')
open('sibs10', 'w').write('\n'.join(sorted(names)) + '\n')
print(len(names), 'siblings')
