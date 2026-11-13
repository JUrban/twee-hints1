#!/usr/bin/env python3
"""timecurve.py RESULTS.tsv [...] [--every 600]: proofs over elapsed time (the t=SECONDS column
loop.py writes), for comparing schedulers at equal wall time and cores."""
import sys
args = [x for x in sys.argv[1:] if not x.startswith('--')]
every = int(sys.argv[sys.argv.index('--every') + 1]) if '--every' in sys.argv else 600
if '--every' in sys.argv:
    args.remove(str(every))
curves = []
for p in args:
    pts = []
    for line in open(p):
        f = line.rstrip('\n').split('\t')
        t = [x for x in f if x.startswith('t=')]
        if t:
            pts.append((int(t[-1][2:]), f[1] == 'THM'))
    pts.sort()
    curves.append(pts)
tmax = max((c[-1][0] for c in curves if c), default=0)
print('t(s)\t' + '\t'.join(args))
for t in list(range(every, tmax + every, every)):
    print(f'{t}\t' + '\t'.join(str(sum(ok for s, ok in c if s <= t)) for c in curves))
