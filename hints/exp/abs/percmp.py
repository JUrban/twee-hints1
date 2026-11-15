"""Compare per-problem AUC files (rulemodel.py/gnn.py --per) on the problems they share.
  python3 abs/percmp.py A.tsv B.tsv ..."""
import sys
F = {f: dict((l.split()[0], float(l.split()[1])) for l in open(f)) for f in sys.argv[1:]}
common = set.intersection(*(set(d) for d in F.values()))
print(f'{len(common)} shared problems')
for f, d in F.items():
    v = [d[n] for n in common]
    print(f'  {f}: mean AUC {sum(v)/len(v):.3f}')
if len(F) == 2:
    a, b = F.values()
    w = sum(b[n] > a[n] for n in common)
    print(f'  second better on {w}/{len(common)}')
