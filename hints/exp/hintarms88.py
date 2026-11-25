"""(25 Nov, exp88b) the 160 s rung's three final-hint arms (climb.py --final-hints-ab, (crc32 >> 3) % 3: pool, sketch
hints only, sketch + 10 nearest siblings) from climb.tsv row FROM on: finals, proofs, final CPU h, proofs per final CPU h,
split by --final-only-ab (bit 2: final only, else climb then final).  Usage: hintarms88.py [CLIMB_TSV] [FROM]"""
import sys, zlib, collections
p = sys.argv[1] if len(sys.argv) > 1 else '/project/hintwork/loops/CLS71/climb.tsv'
fr = int(sys.argv[2]) if len(sys.argv) > 2 else 33404
A = ('pool', 'sketch-only', 'near10')
n, t, cpu = collections.Counter(), collections.Counter(), collections.Counter()
for i, l in enumerate(open(p), 1):
    if i < fr: continue
    w = l.rstrip('\n').split('\t')
    if len(w) < 6 or w[1] != 'final': continue
    k = (A[(zlib.crc32(w[0].encode()) >> 3) % 3], 'final-only' if (zlib.crc32(w[0].encode()) >> 2) % 2 else 'climb')
    for kk in (k, (k[0], 'all')):
        n[kk] += 1; t[kk] += w[3] == 'THM'; cpu[kk] += float(w[5])
for b in ('all', 'climb', 'final-only'):
    for a in A:
        k = (a, b); h = cpu[k] / 3600
        print(f'{a:12s} {b:10s} finals {n[k]:4d} proofs {t[k]:3d} final CPU h {h:6.2f} per CPU h {t[k] / h if h else 0:.2f}')
