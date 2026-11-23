"""condgraph.py OUT [--top 25]: reads exp/condprove.py's OUT/results.tsv. Classes: hard (no proof even with the
earlier siblings assumed), blocked (the proof used unproved siblings), unconditional (it used none). The blocking
graph: a blocked goal falls once every unproved sibling its proof used is proved. A goal's reach: the blocked goals
that fall, to a fixpoint, once it alone is proved. Prints the counts, the reach of the unsolved goals, and the top
ones by reach."""
import sys, collections
sys.path.insert(0, '/project/twee/hints')
a = sys.argv[1:]
top = 25
if '--top' in a:
    i = a.index('--top'); top = int(a[i + 1]); a = a[:i] + a[i + 2:]
OUT = a[0]
R = {}
for l in open(f'{OUT}/results.tsv'):
    f = l.rstrip('\n').split('\t')
    R[f[0]] = f
orig = lambda g: g.rsplit('__goal_', 1)[0]
cls = {}; B = {}
for g, f in R.items():
    if f[1] != 'THM':
        cls[g] = 'hard'
    elif f[3] == '-':
        cls[g] = 'unconditional'
    else:
        cls[g] = 'blocked'
        B[g] = {f'{orig(g)}__goal_{j}' for j in f[3].split(',')}
c = collections.Counter(cls.values())
print(f'{OUT}: {len(R):,} unsolved goals run: hard {c["hard"]:,}, blocked {c["blocked"]:,}, unconditional {c["unconditional"]:,}')
# blockers: which classes are they in (a blocker not in R was not run: it is outside the set or was solved)
bc = collections.Counter(cls.get(x, 'not run') for v in B.values() for x in v)
print('  the blocked goals\' blockers, by class:', ', '.join(f'{k} {v:,}' for k, v in bc.most_common()))
nb = collections.Counter(min(len(v), 4) for v in B.values())
print('  unproved siblings used per blocked goal: ' + ', '.join(f'{k if k < 4 else "4+"}: {nb[k]:,}' for k in sorted(nb)))
allhard = sum(1 for v in B.values() if all(cls.get(x) == 'hard' for x in v))
print(f'  blocked goals whose blockers are all hard: {allhard:,}')
deps = collections.defaultdict(set)
for g, v in B.items():
    for x in v:
        deps[x].add(g)
def reach(x):
    have = {x}; todo = [x]
    while todo:
        y = todo.pop()
        for g in deps.get(y, ()):
            if g not in have and B[g] <= have:
                have.add(g); todo.append(g)
    return len(have) - 1
rc = {g: reach(g) for g in R}
for k in ('hard', 'blocked', 'unconditional'):
    v = sorted((rc[g] for g in R if cls[g] == k), reverse=True)
    if v:
        print(f'  reach of the {k} goals: >=1 {sum(1 for x in v if x >= 1):,}, >=5 {sum(1 for x in v if x >= 5):,}, '
              f'>=20 {sum(1 for x in v if x >= 20):,}; the top 10: {v[:10]}')
# the hard goals together: everything blocked falls once all hard goals are proved?
have = {g for g in R if cls[g] == 'hard'}; todo = list(have); base = len(have)
while todo:
    y = todo.pop()
    for g in deps.get(y, ()):
        if g not in have and B[g] <= have:
            have.add(g); todo.append(g)
print(f'  all hard goals proved would free {len(have) - base:,} of the {c["blocked"]:,} blocked')
# Prover9 proof lines from the previous goal of the original (abs/goal_lines.tsv): how far the step is
gl = {l.split()[0]: int(l.split()[1]) for l in open('/project/hintwork/abs/goal_lines.tsv') if l.strip()}
byo = collections.defaultdict(list)
for x in gl:
    byo[orig(x)].append((int(x.rsplit('_', 1)[1]), x))
prev = {}
for o, v in byo.items():
    v.sort()
    for (_, x), (_, y) in zip(v, v[1:]):
        prev[y] = gl[y] - gl[x]
bins = [(0, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, 10**9)]
row = []
for lo, hi in bins:
    v = [g for g in R if g in prev and lo <= prev[g] <= hi]
    n_ = sum(1 for g in v if cls[g] != 'hard')
    row.append(f'{lo}-{hi if hi < 10**9 else ""}: {n_}/{len(v)}' + (f' ({100*n_/len(v):.0f}%)' if v else ''))
print('  proved (blocked or unconditional) by Prover9 proof lines from the previous goal:', '; '.join(row))
po = collections.Counter(orig(g) for g in R if cls[g] == 'hard')
print('  hard goals by original, the top 10:', ', '.join(f'{o} {n}' for o, n in po.most_common(10)))
print(f'| goal | class | reach | blockers |')
print('|---|---|---:|---|')
for g in sorted(R, key=lambda g: (-rc[g], g))[:top]:
    print(f'| {g} | {cls[g]} | {rc[g]} | {",".join(sorted(x.rsplit("_", 1)[1] for x in B.get(g, ()))) or "-"} |')
