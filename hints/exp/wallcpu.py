"""wallcpu.py [--rows N] [--trusted T] [--walls sets/walls30]: production's last N main-loop runs (loops/UL's last
r*/results.tsv) split by the goal's place: a wall (unsolved, its 30 nearest earlier siblings all trusted), unsolved
with 1-5 or 6+ of those 30 unproved, or trusted. Runs, CPU hours, proofs."""
import collections, glob, sys
a = sys.argv[1:]
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
N = int(opt('--rows', '30000')); TR = opt('--trusted', 'loops/TRUSTNOW/t2139.trusted'); WF = opt('--walls', 'sets/walls30')
T = {l.split()[0] for l in open(TR) if l.strip()}
W = {l.strip() for l in open(WF) if l.strip()}
G = [l.strip() for l in open('sets/all') if l.strip()]
byo = collections.defaultdict(list)
for g in G:
    o, k = g.rsplit('__goal_', 1); byo[o].append(int(k))
def nunp(g):
    o, k = g.rsplit('__goal_', 1); k = int(k)
    below = sorted((j for j in byo[o] if j < k), reverse=True)[:30]
    return sum(1 for j in below if f'{o}__goal_{j}' not in T)
f = sorted(glob.glob('loops/UL/r*/results.tsv'))[-1]
L = open(f).read().splitlines()[-N:]
cpu = collections.Counter(); runs = collections.Counter(); thm = collections.Counter()
for l in L:
    w = l.split('\t')
    try:
        dt = float(w[2])
    except (IndexError, ValueError):
        continue
    g = w[0]
    if g in T:
        c = 'trusted at the list\'s time'
    elif g in W:
        c = 'wall'
    else:
        c = 'unsolved, 1-5 of 30 earlier unproved' if nunp(g) <= 5 else 'unsolved, 6+ of 30 earlier unproved'
    cpu[c] += dt; runs[c] += 1; thm[c] += w[1] == 'THM'
tot = sum(cpu.values())
print(f'{f}: the last {len(L):,} rows; walls {len(W)}')
print('| goals | runs | CPU h (share) | THM | THM per CPU h |')
print('|---|---:|---:|---:|---:|')
for c in sorted(cpu, key=lambda c: -cpu[c]):
    print(f'| {c} | {runs[c]:,} | {cpu[c]/3600:.1f} ({100*cpu[c]/tot:.0f}%) | {thm[c]} | {thm[c]/max(cpu[c]/3600,1e-9):.2f} |')
