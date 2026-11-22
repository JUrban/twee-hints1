#!/usr/bin/env python3
"""(22 Nov 14:36; notes/2026-11-22-hub-roots.md) Production's goals that the from-zero runs never proved, and the
lemma dependencies among them.

  hubroots.py OUT.tsv [--zero Z7,Z8]

For each goal production has (loops/UL/solved.tsv) and none of the from-zero runs has, the earliest kept twee output
(loops/*/r*/out/<goal>, loops/*/out/<goal>) with 'RESULT: Theorem' gives its first recorded proof, and its USEDAXIOMS
line the lemma goals it used (names resolved as exp/trust.py does). A root is such a goal whose first proof used no
other such goal. Its reach is the number of such goals that depend on it through such lemmas, transitively.
Rows: goal, root (1/0), reach, the kept output's dir, the number of such goals it used, production's first own THM
label (or '').
"""
import collections, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lemmas

L = '/project/hintwork/loops'
out = sys.argv[1]
zs = sys.argv[sys.argv.index('--zero') + 1].split(',') if '--zero' in sys.argv else ['Z7', 'Z8']
U = list(dict.fromkeys(l.split('\t')[0] for l in open(f'{L}/UL/solved.tsv')))
Z = set()
for z in zs:
    Z |= {l.split('\t')[0] for l in open(f'{L}/{z}/solved.tsv')}
G = [g for g in U if g not in Z]
Gs = set(G)
outs = {}
for p in glob.glob(f'{L}/*/r*/out/*') + glob.glob(f'{L}/*/out/*'):
    b = os.path.basename(p)
    if b in Gs:
        outs.setdefault(b, []).append(p)


def res(x, g):
    m = re.match(r'(?:lemma|assume)_goal_(\d+)$', x)
    if m:
        return f'{lemmas.split(g)[0]}__goal_{m.group(1)}'
    m = re.match(r'(?:lemma|assume)_knn_\d+_(.+__goal_\d+)$', x) or re.match(r'(?:srclem|skax)_\d+_(.+__goal_\d+)$', x)
    return m.group(1) if m else None


dep, src = {}, {}
for g, ps in outs.items():
    for p in sorted(ps, key=os.path.getmtime):
        t = open(p, errors='replace').read()
        m = re.search(r'^USEDAXIOMS (.*)$', t, re.M)
        if 'RESULT: Theorem' in t and m:
            dep[g] = sorted({u for u in (res(x, g) for x in m.group(1).split()) if u in Gs})
            src[g] = os.path.relpath(p, L).split('/')[0]
            break
lab = {}
for p in sorted(glob.glob(f'{L}/UL/r*/results.tsv')):
    for l in open(p):
        w = l.split('\t', 6)
        if len(w) > 4 and w[1] == 'THM' and w[0] in Gs and w[0] not in lab:
            lab[w[0]] = w[4]
rev = collections.defaultdict(set)
for g, d in dep.items():
    for m_ in d:
        rev[m_].add(g)


def reach(r):
    seen, st = {r}, [r]
    while st:
        for y in rev[st.pop()]:
            if y not in seen:
                seen.add(y); st.append(y)
    return len(seen) - 1


with open(out, 'w') as f:
    for g in sorted(dep, key=lambda g: (bool(dep[g]), -reach(g) if not dep[g] else 0, g)):
        f.write(f'{g}\t{0 if dep[g] else 1}\t{reach(g) if not dep[g] else 0}\t{src[g]}\t{len(dep[g])}\t{lab.get(g, "")}\n')
print(f'{len(G)} goals only production has (from zero: {",".join(zs)}); {len(dep)} with a recorded first proof; '
      f'{sum(1 for d in dep.values() if not d)} roots -> {out}')
