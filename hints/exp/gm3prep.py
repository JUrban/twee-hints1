#!/usr/bin/env python3
"""(20 Nov) exp38b: a sibling run's whole derived rule set as lemma axioms (notes/2026-11-20-given-transfer.md).

For a seeded sample of N unsolved unconditional unit goals: the newest production given log of the same original
(loops/UL/given, by mtime). Its rules (every label: the run's axioms and lemmas, its proof steps, the rules it derived
and did not use) become lemma axioms of the goal's run (SK/<goal>/UL/<source>.ax, which transfer.py run adds); its
proof steps are the hints file. Sound: a given log's rules follow from that run's axioms and proven lemmas, and an
unconditional unit goal's run adds no hypotheses.

  gm3prep.py SKDIR GOALS.tsv [-n 40] [--seed 1]
"""
import os, random, re, sys
sys.path.insert(0, '/project/twee/hints')
import hintsel, lemmas

L = '/project/hintwork/loops'


def main():
    skdir, goals = sys.argv[1], sys.argv[2]
    n = int(sys.argv[sys.argv.index('-n') + 1]) if '-n' in sys.argv else 40
    seed = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 1
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    gd = os.path.join(L, 'UL', 'given')
    newest = {}
    for f in os.listdir(gd):
        o = lemmas.split(f)[0]
        t = os.path.getmtime(os.path.join(gd, f))
        if o not in newest or t > newest[o][0]:
            newest[o] = (t, f)
    cand = []
    for g in (l.strip() for l in open('/project/hintwork/sets/all')):
        if not g or g in S or lemmas.split(g)[0] not in newest:
            continue
        try:
            lits = hintsel.goal_lits(g)
        except Exception:
            continue
        f = newest[lemmas.split(g)[0]][1]
        if len(lits) == 1 and lits[0][0] and lemmas.unit_eq(lemmas.conjecture(f) or '~'):
            cand.append(g)
    random.Random(seed).shuffle(cand)
    with open(goals, 'w') as fo:
        for g in sorted(cand[:n]):
            f = newest[lemmas.split(g)[0]][1]
            rows = [x.rstrip('\n').split('\t') for x in open(os.path.join(gd, f))]
            p = os.path.abspath(os.path.join(skdir, g, 'UL', f))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w') as h:
                h.writelines(f'{x[2]}\t{x[3]}\n' for x in rows if len(x) >= 4 and x[0] == '1')
            with open(p + '.ax', 'w') as h:
                h.writelines(f'{x[2]}\t{x[3]}\n' for x in rows if len(x) >= 4)
            fo.write(f'{g}\t{p}\t0\n')
    print(f'{len(cand)} candidates, {min(n, len(cand))} -> {goals}')


if __name__ == '__main__':
    main()
