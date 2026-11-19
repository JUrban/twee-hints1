# per-label yields in windows of W results rows (time order), from row R
import sys, collections
R = int(sys.argv[2]); W = int(sys.argv[3]); labs = sys.argv[4].split(',')
rows = []
for i, l in enumerate(open(sys.argv[1]), 1):
    if i < R: continue
    f = l.rstrip('\n').split('\t')
    if len(f) < 5: continue
    rows.append((f[4], f[1] != 'NO', float(f[2])))
print('rows', 'all/h', *labs)
for s in range(0, len(rows), W):
    w = rows[s:s + W]; k = collections.Counter(); c = collections.Counter()
    for lab, ok, t in w:
        k[lab] += ok; c[lab] += t
    tot = sum(k.values()) / (sum(c.values()) / 3600)
    print(R + s, f'{tot:5.1f}', *[(f'{k[l] / (c[l] / 3600):5.1f}({k[l]})' if c[l] > 600 else '    -') for l in labs])
