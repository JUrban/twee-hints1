"""Paired comparison of loop arms on the same goals (abs/mab.sh): proved by each, shared, and the
abstract work (WORK considered=, from the out files) on goals both prove.
  python3 abs/mabcmp.py DIR_A DIR_B [ROUND]"""
import math, os, re, sys
R = sys.argv[3] if len(sys.argv) > 3 else 'r1'
def load(d):
    res = {}
    for l in open(os.path.join(d, R, 'results.tsv')):
        x = l.rstrip('\n').split('\t')
        w = None
        try:
            m = re.search(r'^WORK considered=(\d+)', open(os.path.join(d, R, 'out', x[0])).read(), re.M)
            w = int(m.group(1)) if m else None
        except OSError:
            pass
        res[x[0]] = (x[1] == 'THM', w)
    return res
A, B = load(sys.argv[1]), load(sys.argv[2])
both = set(A) & set(B)
pa = {n for n in both if A[n][0]}; pb = {n for n in both if B[n][0]}
print(f'{len(both)} goals run by both: A {len(pa)}, B {len(pb)}, both {len(pa & pb)}, A only {len(pa - pb)}, B only {len(pb - pa)}')
r = [math.log(B[n][1] / A[n][1]) for n in pa & pb if A[n][1] and B[n][1]]
if r:
    r.sort()
    print(f'  shared proofs: B/A work geometric mean {math.exp(sum(r)/len(r)):.3f}, median {math.exp(r[len(r)//2]):.3f}, '
          f'B cheaper on {sum(x < 0 for x in r)}/{len(r)}')
