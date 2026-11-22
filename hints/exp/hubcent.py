#!/usr/bin/env python3
"""(22 Nov 15:24; notes/2026-11-22-hub-roots.md) kNN centrality of unsolved goals: a signal for hubs before they are
proved.

  hubcent.py SOLVED.tsv OUT.tsv [--set sets/all] [-k 30]

For every unsolved unit goal t (in SET, not in SOLVED), its K nearest goals as loop.py's kNN lemmas would pick them
(lemmas.LemmaIndex: idf-weighted Jaccard of goal features, among goals of theories within t's axioms), but with
the unsolved goals counted as if they were proven. An unsolved goal's centrality is the number of unsolved goals
that have it among their K nearest (and the sum of those similarities). Rows: goal, count, sum, sorted by count.
"""
import collections, os, sys
os.environ.setdefault('OMP_NUM_THREADS', '2'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hintsel, lemmas
import pickle

a = sys.argv[1:]
solved_p, out = a[0], a[1]
setp = a[a.index('--set') + 1] if '--set' in a else '/project/hintwork/sets/all'
K = int(a[a.index('-k') + 1]) if '-k' in a else 30
S = {l.split('\t')[0] for l in open(solved_p)}
allg = [l.strip() for l in open(setp) if l.strip()]
names = [n for n in allg if lemmas.lemma_form(n)]
info = pickle.load(open(lemmas.CACHE, 'rb')) if os.path.exists(lemmas.CACHE) else {}
F = {}
for n in names:
    if n in info:
        F[n] = info[n][1]
    else:   # (in memory only: the shared cache is not written)
        try:
            F[n] = frozenset(hintsel.goal_features(n, 3))
        except Exception:
            F[n] = frozenset()
key = {n: lemmas.axiom_key(n) for n in names}
aset = {}
for n in names:
    if key[n] not in aset:
        aset[key[n]] = lemmas.axiom_set(n)
U = [n for n in names if n not in S and F[n]]
Us = set(U)
vocab = {}
for n in names:
    for x in F[n]:
        vocab.setdefault(x, len(vocab))
byk = collections.defaultdict(list)
for n in names:
    if F[n]:
        byk[key[n]].append(n)
cnt, ssum = collections.Counter(), collections.defaultdict(float)
tk = collections.defaultdict(list)
for t in U:
    tk[key[t]].append(t)


def mat(ns):
    r, c = [], []
    for i, n in enumerate(ns):
        for x in F[n]:
            r.append(i); c.append(vocab[x])
    return sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(len(ns), len(vocab)))


for k_, ts in sorted(tk.items(), key=lambda kv: -len(kv[1])):
    pool = [m for kk, A in aset.items() if A <= aset[k_] for m in byk[kk]]
    X = mat(pool)
    df = np.asarray((X > 0).sum(axis=0)).ravel()
    idf = np.where(df > 0, np.log((len(pool) + 1) / np.maximum(df, 1)), 0.0)
    Xw = X.multiply(idf).tocsr()
    wG = np.asarray(Xw.sum(axis=1)).ravel()
    pidx = {m: i for i, m in enumerate(pool)}
    isU = np.array([m in Us for m in pool])
    for c0 in range(0, len(ts), 256):
        T = ts[c0:c0 + 256]
        Ft = mat(T)
        inter = (Ft @ Xw.T).toarray()
        wF = np.asarray(Ft.multiply(idf).sum(axis=1)).ravel()
        union = wF[:, None] + wG[None, :] - inter
        sim = np.where(inter > 0, inter / np.maximum(union, 1e-12), 0.0)
        for i, t in enumerate(T):
            if t in pidx:
                sim[i, pidx[t]] = -1.0
        top = np.argpartition(-sim, min(K, sim.shape[1] - 1), axis=1)[:, :K]
        for i in range(len(T)):
            for j in top[i]:
                if sim[i, j] > 0 and isU[j]:
                    cnt[pool[j]] += 1; ssum[pool[j]] += float(sim[i, j])
    print(f'  key with {len(ts)} unsolved targets, pool {len(pool)}', flush=True)
with open(out, 'w') as f:
    for g in sorted(U, key=lambda g: (-cnt[g], g)):
        f.write(f'{g}\t{cnt[g]}\t{ssum[g]:.3f}\n')
print(f'{len(U)} unsolved unit goals of {len(names)}; {sum(1 for g in U if cnt[g])} are among another\'s {K} nearest '
      f'-> {out}', flush=True)
