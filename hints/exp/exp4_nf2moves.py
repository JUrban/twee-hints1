#!/usr/bin/env python3
"""exp4/nf2moves.py NF.tsv OUT.tsv: the subgoals of nf.py's Mace4-plausible subgoal sets, as moves.py rows of kind
'gen' (sketch.py runs them as goals), minus those that are just a pair of the goal's normal forms (equivalent to
the goal). Detail column: the ids of the sets the subgoal belongs to and their sizes (a set proves the goal when
all its subgoals are proved). Ids start at 2000."""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src, dst = sys.argv[1:]
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        pat = r'\b(X\d+|x\d+)\b'
        return re.sub(pat, f, x) + ' = ' + re.sub(pat, f, y)
    return min(ren(l, r), ren(r, l))
tops = collections.defaultdict(set)
sets = collections.defaultdict(list)
for l in open(src):
    w = l.rstrip('\n').split('\t')
    if w[4] != 'ok': continue
    sets[w[0]].append((w[1], w[5].split('; ')))
for g in sets:
    side = {'L': [], 'R': []}
    for l in open(f'{src}.d/{g}', errors='replace'):
        m = re.match(r'GOALNF ([LR]) fof\(nf, axiom, (.*)\)\.$', l.rstrip('\n'))
        if m: s = m.group(2).replace(' ', ''); side[m.group(1)].append(s[:len(s) // 2])
    tops[g] = {canon(f'{x} = {y}') for x in side['L'] for y in side['R']}
with open(dst, 'w') as f:
    for g in sorted(sets):
        member = collections.defaultdict(list)
        for sid, subs in sets[g]:
            for c in subs:
                if canon(c) not in tops[g]: member[c].append(f'{sid}/{len(subs)}')
        for k, (c, ms) in enumerate(member.items()):
            f.write(f'{g}\t{2000 + k}\tgen\t{c}\tok\tsets {" ".join(ms)}\n')
