"""condcmp.py CTRL ARM... : exp/condprove.py result dirs on the same goals (cond/<X>/results.tsv). For each: rows,
proved, CPU h of twee search runs, proofs per CPU h, proved that CTRL did not (+) and CTRL did that it did not (-);
then the union of all and each arm's goals no other dir proved. A markdown table."""
import sys
D = sys.argv[1:]
R = {}
for d in D:
    R[d] = {}
    for l in open(f'{d}/results.tsv'):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 3:
            R[d][f[0]] = (f[1], float(f[2]))
common = set.intersection(*(set(v) for v in R.values()))
th = {d: {g for g in common if R[d][g][0] == 'THM'} for d in D}
c = D[0]
print(f'{len(common):,} goals in all of {", ".join(D)}')
print('| dir | proved | CPU h | per CPU h | + vs ' + c + ' | − vs ' + c + ' | only here |')
print('|---|---:|---:|---:|---:|---:|---:|')
for d in D:
    cpu = sum(R[d][g][1] for g in common) / 3600
    oth = set().union(*(th[e] for e in D if e != d)) if len(D) > 1 else set()
    print(f'| {d} | {len(th[d])} | {cpu:.2f} | {len(th[d]) / cpu if cpu else 0:.1f} | {len(th[d] - th[c])} | {len(th[c] - th[d])} | {len(th[d] - oth)} |')
u = set().union(*th.values())
print(f'union {len(u)}')
