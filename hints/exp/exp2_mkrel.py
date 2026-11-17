#!/usr/bin/env python3
"""exp2/mkrel.py: relevant extras. A sibling's proof in the pool builds on the lemmas it used (USEDAXIOMS in
ORD's records); when the test run lacks one of those lemmas as an axiom, the sibling's steps after it are out of
reach unless the run derives the lemma. So the relevant extras are the expansions (exp2/xd: steps and statement,
closure within ORD) of the lemmas the siblings used that the run's problem file lacks. Ranked by the number of
siblings that used the lemma; NEAR > 0 counts only siblings at most NEAR goals below the test goal.
Writes h_xr<NEAR>/<g>.hints (captured + relevant extras at the default factor) and rel<NEAR>.tsv: goal, missing
lemmas, extras."""
import collections, os, re, sys
sys.path.insert(0, '/project/twee/hints')
from depcheck import used_lemmas
NEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 0
G = open('goals200').read().split()
U = used_lemmas('/project/hintwork/loops/ORD')
sibs = collections.defaultdict(list)
for s in open('ord_sibs').read().split():
    o, k = s.rsplit('__goal_', 1); sibs[o].append((int(k), s))
def present(g):
    o = g.rsplit('__goal_', 1)[0]; P = set()
    for m in re.finditer(r'fof\((lemma_\S+?),axiom', open(f'/project/hintwork/pg/tb/tmp/{g}.p').read()):
        x = m.group(1)
        a = re.match(r'lemma_knn_\d+_(\S+__goal_\d+)$', x); b = re.match(r'lemma_goal_(\d+)$', x)
        if a: P.add(a.group(1))
        elif b: P.add(f'{o}__goal_{b.group(1)}')
    return P
def lines(s):
    try: return [tuple(x.split('\t')[:2]) for x in open('xd/' + s).read().splitlines() if '\t' in x]
    except OSError: return []
d = f'h_xr{NEAR}'; os.makedirs(d, exist_ok=True)
with open(f'rel{NEAR}.tsv', 'w') as t:
    for g in G:
        o, k = g.rsplit('__goal_', 1); k = int(k)
        base = open(f'/project/hintwork/pg/tb/tmp/{g}.hints').read().splitlines()
        bk = {tuple(x.split('\t')[:2]) for x in base}
        P = present(g); c = collections.Counter()
        for j, s in sibs[o]:
            if NEAR and not (k - NEAR <= j < k): continue
            for m in U.get(s, (set(), []))[0]:
                if m not in P and m != g: c[m] += 1
        seen, ex = set(bk), []
        for m, _ in c.most_common():
            for h in lines(m):
                if h not in seen: seen.add(h); ex.append(h)
        open(f'{d}/{g}.hints', 'w').write('\n'.join(base + ['\t'.join(h) for h in ex]) + '\n')
        t.write(f'{g}\t{len(c)}\t{len(ex)}\n')
