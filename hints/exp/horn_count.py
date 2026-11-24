"""(24 Nov, exp82) Run from /project/hintwork. Goals by kind (unit form / genuine Horn) and proved; proved Horn siblings
among the local heads' 100 previous goals."""
import collections, sys
sys.path.insert(0, '/project/twee/hints')
import lemmas
T = {l.split('\t')[0] for l in open('loops/UL/solved.tsv') if l.strip()}
G = [l.strip() for l in open('sets/all') if l.strip()]
by = collections.defaultdict(list)
for g in G:
    o, k = g.rsplit('__goal_', 1); by[o].append((int(k), g))
kind = {}
for g in G:
    if lemmas.lemma_form(g): kind[g] = 'unit'
    elif lemmas.conjecture(g): kind[g] = 'horn'
    else: kind[g] = 'none'
c = collections.Counter((kind[g], g in T) for g in G)
print('kinds (kind, proved):', sorted(c.items()))
heads = []
for o, v in by.items():
    v.sort()
    for i, (k, g) in enumerate(v):
        if g not in T and (i == 0 or v[i-1][1] in T): heads.append((g, [h for _, h in v[:i]]))
prevhorn = sum(1 for g, b in heads if b and kind[b[-1]] == 'horn')
n100 = [sum(1 for h in b[-100:] if h in T and kind[h] == 'horn') for g, b in heads]
n100u = [sum(1 for h in b[-100:] if h in T and kind[h] == 'unit') for g, b in heads]
print('local heads', len(heads), 'whose previous goal is a proved Horn goal', prevhorn)
print('proved Horn among the 100 previous goals: heads with any', sum(x > 0 for x in n100), 'mean', sum(n100) / len(n100),
      '| proved unit mean', sum(n100u) / len(n100u))
print('heads that are themselves Horn', sum(kind[g] == 'horn' for g, _ in heads))
print('Horn by original (proved):', collections.Counter(g.rsplit('__goal_', 1)[0] for g in G if kind[g] == 'horn' and g in T).most_common(6))
ex = [g for g in G if kind[g] == 'horn' and g in T][:3]
for g in ex: print(' ', g, lemmas.conjecture(g)[:160])
