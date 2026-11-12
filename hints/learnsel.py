#!/usr/bin/env python3
"""Learned hint ranking on top of kNN candidates.

For a target goal, candidates are the hints of the K most similar solved
goals. Each (target, hint) pair gets a feature vector; a logistic model
predicts whether the hint occurs in the target's own proof.

Offline evaluation: train on problems of some originals, test recall@N on
the other originals (labels = the held-out problem's own proof).
"""
import collections, math, os, random, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feats, hintsel

FEATS = ['knn', 'knnmax', 'nnb', 'logfreq', 'size', 'nvars', 'ovl_goal', 'ovl_frac',
         'is_goal', 'rank', 'eqsides']

class Ranker:
    def __init__(self, knn: hintsel.KNN):
        self.knn = knn
        self.freq = collections.Counter(h for L in knn.hints.values() for h in set(L))
        self.ngoal = collections.Counter(L[-1] for L in knn.hints.values() if L)
        self.hfeat = {}
        self.w = None

    def hint_feats(self, h):
        f = self.hfeat.get(h)
        if f is None:
            l, r = h.split('\t')
            f = (feats.features(l, r, 2), sum(1 for c in l + r if c.isalpha() and c.islower()),
                 len(set(x for x in (l + ',' + r).replace('(', ',').replace(')', ',').split(',') if x[:1].isupper())))
            self.hfeat[h] = f
        return f

    def candidates(self, name, k=30, ncand=400, exclude=None):
        idf = self.knn.idf()
        F = hintsel.goal_features(name, self.knn.depth)
        F2 = hintsel.goal_features(name, 2)
        sims = []
        for m, G in self.knn.feats.items():
            if m == name or (exclude and exclude(m)):
                continue
            i = sum(idf.get(x, 0) for x in F & G)
            if i == 0:
                continue
            u = sum(idf.get(x, 0) for x in F | G)
            sims.append((i / u, m))
        sims.sort(reverse=True)
        sc = collections.Counter(); mx = {}; nb = collections.Counter()
        for s, m in sims[:k]:
            for h in self.knn.hints[m]:
                sc[h] += s; nb[h] += 1
                mx[h] = max(mx.get(h, 0), s)
        cands = sc.most_common(ncand)
        X = []
        for rank, (h, s) in enumerate(cands):
            hf, size, nv = self.hint_feats(h)
            inter = hf & F2
            ov = sum(idf.get(x, 1.0) for x in inter)
            un = sum(idf.get(x, 1.0) for x in hf | F2) or 1
            X.append([s, mx[h], nb[h], math.log(1 + self.freq[h]), size, nv, ov / un,
                      len(inter) / max(1, len(hf)), 1.0 if self.ngoal[h] else 0.0,
                      math.log(1 + rank), 1.0 if h.split('\t')[0][:1].isupper() else 0.0])
        return [h for h, _ in cands], np.array(X, dtype=float)

    def score(self, X):
        if self.w is None:
            return X[:, 0]
        Z = (X - self.mu) / self.sd
        return Z @ self.w[:-1] + self.w[-1]

    def fit(self, XS, YS, l2=1.0, iters=300):
        X = np.vstack(XS); y = np.concatenate(YS)
        self.mu = X.mean(0); self.sd = X.std(0) + 1e-9
        Z = (X - self.mu) / self.sd
        Z = np.hstack([Z, np.ones((len(Z), 1))])
        w = np.zeros(Z.shape[1])
        # Newton iterations for L2-regularised logistic regression
        for _ in range(30):
            p = 1 / (1 + np.exp(-(Z @ w)))
            g = Z.T @ (p - y) + l2 * np.r_[w[:-1], 0]
            H = (Z * (p * (1 - p))[:, None]).T @ Z + l2 * np.eye(len(w))
            w -= np.linalg.solve(H, g)
        self.w = w

    def select(self, name, topn=100, k=30, ncand=400):
        hs, X = self.candidates(name, k, ncand)
        if not hs:
            return []
        s = self.score(X)
        order = np.argsort(-s)
        return [hs[i] for i in order[:topn]]

def evaluate(hintdir, seed=1, ntest=300):
    knn = hintsel.KNN(hintdir)
    rk = Ranker(knn)
    names = [n for n in knn.hints if len(knn.hints[n]) >= 10]
    origs = sorted(set(n.split('__goal_')[0] for n in names))
    random.seed(seed); random.shuffle(origs)
    test_o = set(origs[:len(origs) // 3])
    train = [n for n in names if n.split('__goal_')[0] not in test_o]
    test = [n for n in names if n.split('__goal_')[0] in test_o]
    random.shuffle(train); random.shuffle(test)
    XS, YS = [], []
    for n in train[:1500]:
        own = set(knn.hints[n])
        hs, X = rk.candidates(n)
        if len(hs) == 0:
            continue
        XS.append(X); YS.append(np.array([h in own for h in hs], dtype=float))
    rk.fit(XS, YS)
    print('weights', dict(zip(FEATS + ['bias'], np.round(rk.w, 2))))
    for topn in [50, 100, 200]:
        r0, r1 = [], []
        for n in test[:ntest]:
            own = set(knn.hints[n])
            hs, X = rk.candidates(n)
            if len(hs) == 0:
                continue
            base = set(hs[:topn])
            s = rk.score(X); order = np.argsort(-s)
            lrn = set(hs[i] for i in order[:topn])
            r0.append(len(own & base) / len(own)); r1.append(len(own & lrn) / len(own))
        print(f'top{topn}: recall knn {np.mean(r0):.3f} learned {np.mean(r1):.3f} (n={len(r0)})')
    return rk

if __name__ == '__main__':
    evaluate(sys.argv[1])
