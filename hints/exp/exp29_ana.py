# exp29: PGD (explored 5 s lemma members) against PGC and PGA, half1 from zero, 2 hours: levels and one-arm goals
import collections, sys
L = '/project/hintwork/loops/'
half1 = {l.strip() for l in open('/project/hintwork/sets/half1') if l.strip()}
def solved(a):
    return {l.split('\t')[0] for l in open(L + a + '/solved.tsv')} & half1
def levels(a):
    n = collections.Counter(); p = collections.Counter(); c = collections.Counter()
    for l in open(L + a + '/r1/results.tsv'):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5: continue
        n[f[4]] += 1; p[f[4]] += f[1] != 'NO'; c[f[4]] += float(f[2])
    for k in sorted(n):
        print(f'  {a} {k:8s} runs {n[k]:6d} proofs {p[k]:6d} CPU h {c[k]/3600:6.2f} per CPU h {p[k]/max(1e-9, c[k]/3600):7.1f}')
A, C, D = solved('PGA'), solved('PGC'), solved('PGD')
for x, X in (('PGA', A), ('PGC', C)):
    print(f'PGD {len(D)} {x} {len(X)}: only PGD {len(D - X)}, only {x} {len(X - D)}, union {len(D | X)}')
print('union of all three', len(A | C | D), ' only PGD (in neither)', len(D - A - C))
levels('PGD')
prov = {}
for l in open(L + 'PGD/r1/results.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 5 and f[1] != 'NO' and f[0] not in prov:
        prov[f[0]] = f[4]
print('PGD-only (against PGC) by level', collections.Counter(prov.get(g, 'transfer/other') for g in D - C).most_common())
print('PGD-only (against both) by level', collections.Counter(prov.get(g, 'transfer/other') for g in D - A - C).most_common())
