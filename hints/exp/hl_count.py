# how many new hints the hl variant adds in production (UL): kNN lemmas' proof steps not in the goal's original pool
import sys, os, random, collections, time
sys.path.insert(0, '/project/twee/hints')
import lemmas
D = 'loops/UL'
solved = {l.split('\t')[0]: 1 for l in open(D + '/solved.tsv')}
t = time.time()
ix = lemmas.LemmaIndex(sorted(solved), subsets=True)
src = {o: set(v) for o, v in lemmas.by_original(solved).items()}
print('index', round(time.time() - t, 1), 's', file=sys.stderr)
def steps(n):
    try:
        return [tuple(x.split('\t')[:2]) for x in open(os.path.join(D, 'hints', n)).read().splitlines()]
    except OSError:
        return []
names = [l.strip() for l in open('sets/all') if l.strip()]
uns = [n for n in names if n not in solved and '__goal_' in n]
random.seed(1); smp = random.sample(uns, 30)
for n in smp:
    o, _ = lemmas.split(n)
    pool = set()
    for m in solved:
        if m.startswith(o + '__goal_'):
            pool.update(steps(m))
    picks = lemmas.knn_picks(n, src, 6, ix, 30, True)
    cross = [p for p in picks if not p.startswith(o + '__goal_')]
    new = set()
    for p in picks:
        new.update(s for s in steps(p)[:300] if s not in pool)
    print(n, 'pool', len(pool), 'picks', len(picks), 'cross', len(cross), 'new', len(new))
