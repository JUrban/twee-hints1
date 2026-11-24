"""(24 Nov, exp82; notes/2026-11-24-horn-lemmas.md) Run from /project/hintwork: the unsolved local heads by proved Horn
siblings in their window (100 proved before, 30 after), and cond/EXP82.set: 60 of those with at least 2, not in
exp81's set, random with seed 82. The code that made the set at 07:26 (it read loops/UL/solved.tsv then).
(09:33, exp82c) --seed N, --exclude F,G (default cond/EXP81.set), --out FILE (default cond/EXP82.set; written with --write)."""
import sys, collections, random
sys.path.insert(0, '/project/twee/hints'); import lemmas
T = {l.split('\t')[0] for l in open('loops/UL/solved.tsv') if l.strip()}
G = [l.strip() for l in open('sets/all') if l.strip()]
by = collections.defaultdict(list)
for g in G:
    o, k = g.rsplit('__goal_', 1); by[o].append(int(k))
def horn(g): return g in T and not lemmas.lemma_form(g) and lemmas.conjecture(g)
heads, cnt = [], {}
for o, ks in by.items():
    ks.sort()
    for i, k in enumerate(ks):
        g = f'{o}__goal_{k}'
        if g in T or not (i == 0 or f'{o}__goal_{ks[i-1]}' in T): continue
        before = [j for j in ks[:i] if f'{o}__goal_{j}' in T][-100:]   # unit window is ~ the 100 nearest proved; Horn ones on top
        after = [j for j in ks[i+1:] if f'{o}__goal_{j}' in T][:30]
        cnt[g] = sum(1 for j in before + after if horn(f'{o}__goal_{j}'))
        heads.append(g)
c = collections.Counter(min(cnt[g], 5) for g in heads)
print('heads', len(heads), 'by Horn siblings in window (5 = 5+):', sorted(c.items()))
def opt(k, d):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SEED = int(opt('--seed', '82')); OUT = opt('--out', 'cond/EXP82.set')
E81 = set()
for f in opt('--exclude', 'cond/EXP81.set').split(','):
    E81 |= {l.strip() for l in open(f) if l.strip()}
cand = [g for g in heads if cnt[g] >= 2 and g not in E81]
random.seed(SEED); random.shuffle(cand)
pick = sorted(cand[:60])
if '--write' in sys.argv:
    open(OUT, 'w').write(''.join(g + '\n' for g in pick))
print('candidates (>= 2, not in exp81)', len(cand), 'picked', len(pick), 'Horn mean', sum(cnt[g] for g in pick) / len(pick),
      'originals', len({g.rsplit('__goal_', 1)[0] for g in pick}))
