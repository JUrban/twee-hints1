#!/usr/bin/env python3
"""(20 Nov 13:50) Why a from-zero half run stops short of production (notes/2026-11-20-half-gap.md).

For the goals of SET that production (loops/UL) proved and none of the from-zero ARMS did: which production mechanism
proved them first (the results label of loops/UL/r*/results.tsv, else a side writer's transfer.tsv), and, for
production's 5 s level (L0) proofs with a kept output, whether the lemmas they used (USEDAXIOMS: siblings
lemma_goal_J, kNN lemma_knn_I_<goal>) were proved in the first arm, are other goals of SET, or lie outside SET.

  halfgap.py SET ARM[,ARM...]      e.g. halfgap.py sets/half2 P2E,P2F
"""
import ast, collections, glob, os, re, statistics, sys
sys.path.insert(0, '/project/twee/hints')
import lemmas

L = '/project/hintwork/loops'


def solved(d):
    return {l.split('\t')[0] for l in open(f'{L}/{d}/solved.tsv') if l.strip()}


def main():
    st, arms = sys.argv[1], sys.argv[2].split(',')
    H = {l.strip() for l in open(st) if l.strip()}
    U = solved('UL') & H
    A = set().union(*(solved(a) for a in arms)) & H
    E = solved(arms[0])
    G = U - A
    print(f'{st}: {len(H)} goals; production {len(U)}, {"|".join(arms)} {len(A)}; production only {len(G)}, '
          f'from zero only {len(A - U)}')
    lab = {}
    for p in sorted(glob.glob(f'{L}/UL/r*/results.tsv')):
        r = p.split('/')[-2]
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5 and w[1] == 'THM' and w[0] in G and w[0] not in lab:
                lab[w[0]] = (r, w[4])
    side = {}
    for p in glob.glob(f'{L}/*/transfer.tsv'):
        d = p.split('/')[-2]
        for l in open(p, errors='replace'):
            w = l.split('\t')
            if len(w) >= 2 and w[1] == 'THM' and w[0] in G and w[0] not in lab and w[0] not in side:
                side[w[0]] = d
    c = collections.Counter('V*' if v[1].startswith('V') else v[1] for v in lab.values())
    c.update(side.values())
    c['unknown'] = len(G - set(lab) - set(side))
    print('first proved by: ' + ', '.join(f'{k} {v}' for k, v in c.most_common(12)))
    num = lambda g: int(g.rsplit('_', 1)[1])
    print(f'median goal number: production only {statistics.median(num(g) for g in G)}, '
          f'from zero {statistics.median(num(g) for g in A)}')
    kinds, per = collections.Counter(), collections.Counter()
    for g, (r, lb) in lab.items():
        if lb != 'L0':
            continue
        p = f'{L}/UL/{r}/out/{g}'
        if not os.path.exists(p):
            per['no kept output'] += 1
            continue
        m = re.search(r'USEDAXIOMS(.*)', open(p, errors='replace').read())
        if not m:
            per['no USEDAXIOMS'] += 1
            continue
        o = lemmas.split(g)[0]
        where_all = set()
        for x in m.group(1).split():
            d = kind = None
            mm = re.match(r'lemma_goal_(\d+)$', x)
            if mm:
                d, kind = f'{o}__goal_{mm.group(1)}', 'sibling'
            mm = re.match(r'lemma_knn_\d+_(.+__goal_\d+)$', x)
            if mm:
                d, kind = mm.group(1), 'kNN'
            if d is None:
                continue
            where = f'in {arms[0]}' if d in E else ('in the set, not proved' if d in H else 'outside the set')
            kinds[(kind, where)] += 1
            where_all.add(where)
        per['uses a lemma outside the set' if 'outside the set' in where_all else
            ('uses an unproved lemma of the set' if 'in the set, not proved' in where_all else
             f'all its lemmas in {arms[0]} (or none)')] += 1
    print('L0 proofs\' lemmas: ' + ', '.join(f'{k[0]} {k[1]} {v}' for k, v in sorted(kinds.items())))
    print('L0 proofs: ' + ', '.join(f'{k} {v}' for k, v in per.most_common()))


if __name__ == '__main__':
    main()
