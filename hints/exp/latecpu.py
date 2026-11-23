#!/usr/bin/env python3
"""(23 Nov) Where a from-zero run's CPU went, hour by hour: its runs (OUT/r1/results.tsv rows: goal, status, CPU s,
..., t=<s since start>) split by the goal's fate: solved by the run itself, solved only by a reference list (e.g.
production's trusted list), or by neither.

  latecpu.py OUT REFLIST [--hours 6]
"""
import argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('ref'); ap.add_argument('--hours', type=int, default=6)
ap.add_argument('--names', default='/project/hintwork/sets/all')
o = ap.parse_args()
ref = set(open(o.ref).read().split())
own = {l.split('\t')[0] for l in open(f'{o.out}/solved.tsv')}
alln = set(open(o.names).read().split())
K = ('own', 'ref only', 'neither')
cpu = collections.defaultdict(float); n = collections.Counter(); thm = collections.Counter()
import os
off = (sorted((int(r), float(x)) for r, x in (l.split() for l in open(o.out.rstrip('/') + '.toffset') if l.strip()))
       if os.path.exists(o.out.rstrip('/') + '.toffset') else [])   # (a continued run: see abscurve.py's toffsets)
for i, l in enumerate(open(f'{o.out}/r1/results.tsv', errors='replace')):
    w = l.rstrip('\n').split('\t')
    if len(w) < 6: continue
    try: c = float(w[2])
    except ValueError: continue
    t = next((int(x[2:]) for x in w if x.startswith('t=')), None)
    if t is None: continue
    t += int(next((x for r, x in reversed(off) if i >= r), 0))
    h = min(t // 3600, o.hours - 1)
    k = K[0] if w[0] in own else K[1] if w[0] in ref else K[2]
    cpu[h, k] += c; n[h, k] += 1; thm[h, k] += w[1] == 'THM'
print(f'{o.out}: own {len(own & alln):,}, {o.ref} only {len((ref - own) & alln):,}, neither {len(alln - ref - own):,}')
print('| hour | ' + ' | '.join(f'{k}: runs, CPU h (share)' for k in K) + ' | own THM |')
print('|---:|' + '---:|' * (len(K) + 1))
for h in range(o.hours):
    tot = sum(cpu[h, k] for k in K) or 1
    print(f'| {h} | ' + ' | '.join(f'{n[h,k]:,}, {cpu[h,k]/3600:.2f} ({cpu[h,k]/tot:.0%})' for k in K) + f' | {thm[h,K[0]]:,} |')
