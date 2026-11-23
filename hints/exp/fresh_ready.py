"""fresh_ready.py LOOP [--from MIN] [--to MIN] [--names sets/all] [--out TSV]: does a kNN readiness signal predict a
goal's first main-loop run better than the gap order the loop uses for first runs?

For each goal's first main-loop run (r1/results.tsv, t= in [FROM, TO) minutes), against the goals of its axiom
key proved before the run (first THM row's t=, or else the hints file's mtime against config.json):
  s1   the highest kNN similarity (lemmas.LemmaIndex's idf-weighted Jaccard of goal features; idf here is over all
       goals of the key, fixed, not the loop's changing one);
  s10  the 10th highest;
  n30  how many goals proved in the 30 minutes before the run score above the 10th highest of those proved before
       that (the --knn-ctx test, for a goal never run);
  gap  places after the nearest goal proved below it in its original (the loop's first-run order, with --retry-gap
       3: up to 3 'near', the rest 'far').
Prints each signal's AUC for the run's success, by hour, and the success of the top quarter of each hour's first
runs by each order. No twee runs; numpy/scipy on 2 threads."""
import os, sys, collections, math, pickle
os.environ.setdefault('OMP_NUM_THREADS', '2'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
import numpy as np, scipy.sparse as sp
sys.path.insert(0, '/project/twee/hints')
import lemmas
a = sys.argv[1:]; L = '/project/hintwork/loops'
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
frm = float(opt('--from', '60')) * 60; to = float(opt('--to', '360')) * 60
names = opt('--names', '/project/hintwork/sets/all'); out = opt('--out', '')
D = f'{L}/{a[0]}'
G = [l.strip() for l in open(names) if l.strip()]
info = pickle.load(open(lemmas.CACHE, 'rb'))
G = [g for g in G if g in info]
t0 = os.stat(f'{D}/config.json').st_mtime
pt = {}
for g in os.listdir(f'{D}/hints'):
    pt[g] = os.stat(f'{D}/hints/{g}').st_mtime - t0
first = {}
for l in open(f'{D}/r1/results.tsv'):
    f = l.rstrip('\n').split('\t')
    t = next((float(x[2:]) for x in f if x.startswith('t=')), None)
    if t is None:
        continue
    if f[0] not in first:
        first[f[0]] = (t, f[1] == 'THM')
    if f[1] == 'THM':
        pt[f[0]] = min(pt.get(f[0], 1e18), t)
# gap at time t: the original's goals in goal order
byo = collections.defaultdict(list)
for g in G:
    o, k = lemmas.split(g); byo[o].append((int(k), g))
for o in byo:
    byo[o].sort()
pos = {g: (o, i) for o, v in byo.items() for i, (_, g) in enumerate(v)}
def gap(g, t):
    o, i = pos[g]; v = byo[o]
    for j in range(i - 1, -1, -1):
        if pt.get(v[j][1], 1e18) < t:
            return i - j
    return 10 ** 6
runs = [(g, t, ok) for g, (t, ok) in first.items() if frm <= t < to and g in info]
bykey = collections.defaultdict(list)
for g in G:
    bykey[info[g][0]].append(g)
feat = {}
for key, members in bykey.items():
    R = [r for r in runs if info[r[0]][0] == key]
    if not R:
        continue
    df = collections.Counter(x for m in members for x in info[m][1])
    idf = {x: math.log((len(members) + 1) / c) for x, c in df.items()}
    col = {x: i for i, x in enumerate(idf)}
    w = np.array([idf[x] for x in col])
    def mat(gs):
        ri, ci = [], []
        for r_, g in enumerate(gs):
            for x in info[g][1]:
                ri.append(r_); ci.append(col[x])
        return sp.csr_matrix((np.ones(len(ri)), (ri, ci)), shape=(len(gs), len(col)))
    C = [m for m in members if m in pt]
    XC = mat(C); wC = XC @ w; ptC = np.array([pt[m] for m in C]); iC = {m: i for i, m in enumerate(C)}
    for s in range(0, len(R), 400):
        chunk = R[s:s + 400]
        XR = mat([r[0] for r in chunk]); wR = XR @ w
        inter = (XR.multiply(w) @ XC.T).toarray()
        union = wR[:, None] + wC[None, :] - inter
        S = np.where(inter > 0, inter / np.maximum(union, 1e-12), 0.0)
        for i, (g, t, ok) in enumerate(chunk):
            m_ = ptC < t
            if g in iC:
                m_[iC[g]] = False
            sv = np.sort(S[i][m_])[::-1]
            s1 = sv[0] if len(sv) else 0.0; s10 = sv[9] if len(sv) >= 10 else 0.0
            old = m_ & (ptC < t - 1800)
            so = np.sort(S[i][old])[::-1]; th = so[9] if len(so) >= 10 else 0.0
            n30 = int(np.sum(S[i][m_ & ~old] > th))
            feat[g] = (t, ok, s1, s10, n30, gap(g, t))
def auc(xs, ys):
    """AUC of score xs for labels ys (ties count half)."""
    p = sorted(zip(xs, ys)); n1 = sum(ys); n0 = len(ys) - n1
    if not n1 or not n0:
        return float('nan')
    r, i, acc = 1, 0, 0.0
    while i < len(p):
        j = i
        while j < len(p) and p[j][0] == p[i][0]:
            j += 1
        acc += sum(y for _, y in p[i:j]) * (i + 1 + j) / 2
        i = j
    return (acc - n1 * (n1 + 1) / 2) / (n1 * n0)
sig = {'s1': lambda v: v[2], 's10': lambda v: v[3], 'n30': lambda v: v[4], '-gap': lambda v: -v[5],
       's10+n30': lambda v: v[3] + 0.02 * v[4]}
print(a[0], f'first runs at {frm/60:g}-{to/60:g} min:', len(feat), 'proved', sum(v[1] for v in feat.values()))
hours = sorted({int(v[0] // 3600) for v in feat.values()})
print('| hour | runs | proved | ' + ' | '.join(f'AUC {k}' for k in sig) + ' | ' + ' | '.join(f'top 25% by {k}' for k in sig) + ' |')
print('|' + '---:|' * (3 + 2 * len(sig)))
for h in hours + ['all']:
    V = [v for v in feat.values() if h == 'all' or int(v[0] // 3600) == h]
    ys = [int(v[1]) for v in V]
    row = [str(h), f'{len(V):,}', f'{sum(ys):,} ({100*sum(ys)/max(1,len(V)):.0f}%)']
    row += [f'{auc([f(v) for v in V], ys):.3f}' for f in sig.values()]
    for f in sig.values():
        top = sorted(V, key=lambda v: -f(v))[:max(1, len(V) // 4)]
        row.append(f'{100*sum(v[1] for v in top)/len(top):.0f}%')
    print('| ' + ' | '.join(row) + ' |')
if out:
    with open(out, 'w') as fo:
        for g, v in sorted(feat.items()):
            fo.write('\t'.join([g] + [f'{x:.4g}' if isinstance(x, float) else str(int(x)) for x in v]) + '\n')
