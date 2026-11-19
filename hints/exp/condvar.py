# for each proof by the given labels from row R on: which variant labels had failed on that goal in the same context
import sys, collections
R = int(sys.argv[2]); labs = set(sys.argv[3].split(','))
tried = collections.defaultdict(set); res = collections.Counter(); prev_any = collections.Counter()
for i, l in enumerate(open(sys.argv[1]), 1):
    f = l.rstrip('\n').split('\t')
    if len(f) < 6: continue
    c = next((x for x in f[5:] if x.startswith('c=')), None)
    key = (f[0], c)
    if i >= R and f[4] in labs and f[1] != 'NO':
        before = sorted(x for x in tried[key] if x.startswith('V'))
        res[(f[4], len(before))] += 1
        for b in before: prev_any[(f[4], b)] += 1
    tried[key].add(f[4])
for k, v in sorted(res.items()): print(k[0], 'proved after', k[1], 'failed variants:', v)
for k, v in sorted(prev_any.items()): print('  ', k[0], 'after', k[1], v)
