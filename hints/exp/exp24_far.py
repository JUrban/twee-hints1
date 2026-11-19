#!/usr/bin/env python3
"""exp24/far.py SEED N: UL's unsolved goals of sets/all split by loop.py's may_deepen (--frontier 1, --line-gaps 80,80:
at most 1 place or at most 80 proof lines after the nearest proven goal below). Writes far.tsv (goal, places, lines,
max CPU s of any run in r5, deepest level label) for the far ones and sample.txt: N far goals at random (SEED), each
with no run over 30 CPU s."""
import collections, random, sys
sys.path.insert(0, '/project/twee/hints')
import lemmas
seed, N = int(sys.argv[1]), int(sys.argv[2])
UL = '/project/hintwork/loops/UL'
names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
solved = {l.split('\t')[0] for l in open(f'{UL}/solved.tsv')}
gl = {}
for l in open('/project/hintwork/abs/goal_lines.tsv'):
    n, x = l.split(); gl[n] = int(x)
orig = lambda n: n.rsplit('__goal_', 1)[0]
byo = collections.defaultdict(list)
for n in set(names) | solved:
    if '__goal_' in n: byo[orig(n)].append(n)
os_ = {orig(n) for n in names}
g = {}
for o, L in byo.items():
    if o not in os_: continue
    L.sort(key=lambda n: lemmas.split(n)[1]); last = None
    for i, n in enumerate(L):
        if n in solved: last = i
        elif last is None: g[n] = (10**6, 10**6)
        else: g[n] = (i - last, gl[n] - gl[L[last]])
mx = collections.defaultdict(float); lv = {}
for l in open(f'{UL}/r5/results.tsv'):
    w = l.rstrip('\n').split('\t')
    if len(w) < 5: continue
    try: c = float(w[2])
    except ValueError: continue
    if c > mx[w[0]]: mx[w[0]] = c; lv[w[0]] = w[4]
uns = [n for n in names if n not in solved and n in g]
far = [n for n in uns if not (g[n][0] <= 1 or g[n][1] <= 80)]
with open('far.tsv', 'w') as f:
    for n in sorted(far): f.write(f'{n}\t{g[n][0]}\t{g[n][1]}\t{mx[n]:.1f}\t{lv.get(n, "-")}\n')
cand = sorted(n for n in far if mx[n] <= 30)
print(f'unsolved {len(uns)}, far {len(far)}, far with no run over 30 CPU s {len(cand)}; near {len(uns) - len(far)}, '
      f'near with no run over 30 s {sum(1 for n in uns if n not in far and mx[n] <= 30)}')
print('far by places:', collections.Counter(min(g[n][0], 99) for n in far).most_common(12))
random.Random(seed).shuffle(cand)
open('sample.txt', 'w').write(''.join(n + '\n' for n in sorted(cand[:N])))
print('sample originals:', collections.Counter(orig(n) for n in cand[:N]).most_common(8))
