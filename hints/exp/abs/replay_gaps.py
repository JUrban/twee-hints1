import collections, sys
sys.path.insert(0, '/project/twee/hints')
import lemmas
def orig_of(n): return n.rsplit('__goal_', 1)[0]
names = [l.strip() for l in open('sets/all') if l.strip()]
gl = {}
for l in open('abs/goal_lines.tsv'):
    n, x = l.split(); gl[n] = int(x)
rows = [l.rstrip('\n').split('\t') for l in open('loops/UL/r5/results.tsv')]
N = int(sys.argv[1])   # number of trailing rows (this session)
sess = rows[-N:]
sessthm = {r[0] for r in sess if r[1] == 'THM'}
srows = [l.split('\t')[0] for l in open('loops/UL/solved.tsv')]
solved = set(srows) - sessthm   # approx: synced ones included from start
byo = collections.defaultdict(list)
for n in set(names) | solved:
    byo[orig_of(n)].append(n)
for o in byo: byo[o].sort(key=lambda n: lemmas.split(n)[1])
pos = {n: (o, i) for o, L in byo.items() for i, n in enumerate(L)}
def gap(n):
    o, i = pos[n]; L = byo[o]
    for j in range(i - 1, -1, -1):
        if L[j] in solved: return (i - j, gl[n] - gl[L[j]])
    return (10**6, 10**6)
bins = [(0, 13), (14, 21), (22, 40), (41, 80), (81, 10**5), (10**6, 10**6)]
st = collections.defaultdict(lambda: [0, 0, 0.0])
for r in sess:
    n, res, dt, lev = r[0], r[1], float(r[2]), r[4]
    g = gap(n)
    b = next(b for b in bins if b[0] <= g[1] <= b[1])
    s = st[(lev, b)]; s[0] += 1; s[1] += res == 'THM'; s[2] += dt
    if res == 'THM': solved.add(n)
for k in sorted(st):
    c, t, d = st[k]
    print(k, c, t, f'{100*t/c:.0f}%', f'{1000*t/d:.1f}/ks')
