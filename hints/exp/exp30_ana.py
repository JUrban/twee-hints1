# exp30: P2D (solve_new.sh's new defaults) against P2A (the 17 Nov system), half2 from zero, 2 hours, both at once:
# one-arm goals, P2D's levels, and where its one-arm goals were proved (as exp29_ana.py)
import collections
L = '/project/hintwork/loops/'
half2 = {l.strip() for l in open('/project/hintwork/sets/half2') if l.strip()}
def solved(a):
    return {l.split('\t')[0] for l in open(L + a + '/solved.tsv')} & half2
def levels(a):
    n = collections.Counter(); p = collections.Counter(); c = collections.Counter()
    for l in open(L + a + '/r1/results.tsv'):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5: continue
        n[f[4]] += 1; p[f[4]] += f[1] != 'NO'; c[f[4]] += float(f[2])
    for k in sorted(n):
        print(f'  {a} {k:8s} runs {n[k]:6d} proofs {p[k]:6d} CPU h {c[k]/3600:6.2f} per CPU h {p[k]/max(1e-9, c[k]/3600):7.1f}')
A, D = solved('P2A'), solved('P2D')
print(f'P2D {len(D)} P2A {len(A)}: only P2D {len(D - A)}, only P2A {len(A - D)}, union {len(D | A)}')
levels('P2A'); levels('P2D')
for arm, X, Y in (('P2D', D, A), ('P2A', A, D)):
    prov = {}
    for l in open(L + arm + '/r1/results.tsv'):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 5 and f[1] != 'NO' and f[0] not in prov:
            prov[f[0]] = f[4]
    print(f'{arm}-only by level', collections.Counter(prov.get(g, 'transfer/other') for g in X - Y).most_common())
