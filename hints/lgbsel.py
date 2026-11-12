#!/usr/bin/env python3
"""ENIGMA-style learned hint ranking with LightGBM.

Candidates: hints of the K goal-nearest solved problems (learnsel.Ranker).
Row of a (target, hint) pair = pair features (kNN score, frequency, ...)
+ enigmatic features of the hint ('h:' block) + of the goal ('g:' block)
+ overlap counts of the two (shared vertical/horizontal/symbol features).
Label: the hint is a lemma of the target's own proof.

Usage: lgbsel.py HINTDIR [--obj binary|lambdarank] [--save MODEL]
"""
import argparse, collections, math, os, pickle, random, sys
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enigfeats, hintsel, learnsel

NPAIR = len(learnsel.FEATS)

class LGBRanker:
    def __init__(self, knn, k=30, ncand=600):
        self.base = learnsel.Ranker(knn)
        self.knn = knn
        self.k, self.ncand = k, ncand
        self.vocab = enigfeats.Vocab()
        self.hcache = {}
        self.gcache = {}
        self.model = None

    def hint_feats(self, h):
        f = self.hcache.get(h)
        if f is None:
            l, r = h.split('\t')
            f = self.hcache[h] = enigfeats.features(l, r)
        return f

    def goal_feats(self, name):
        f = self.gcache.get(name)
        if f is None:
            f = collections.Counter()
            try:
                lits = hintsel.goal_lits(name)
            except Exception:
                l, r = self.knn.hints[name][-1].split('\t')
                lits = [(True, l, r)]
            for pos, l, r in lits:
                for k, v in enigfeats.features(l, r).items():
                    f[('' if pos else 'n') + k] += v
            f['Llits'] = len(lits)
            self.gcache[name] = f
        return f

    def rows(self, name):
        hs, P = self.base.candidates(name, self.k, self.ncand)
        if not hs:
            return hs, None
        g = self.goal_feats(name)
        gcols = [(self.vocab.get('g:' + k), v) for k, v in g.items()]
        gcols = [(i, v) for i, v in gcols if i is not None]
        gkeys = set(k for k in g if k[0] in 'VHC')
        data, ind, ptr = [], [], [0]
        for j, h in enumerate(hs):
            cols = {}
            for i in range(NPAIR):
                cols[i] = P[j, i]
            hf = self.hint_feats(h)
            for k, v in hf.items():
                i = self.vocab.get('h:' + k)
                if i is not None:
                    cols[NPAIR + 3 + i] = v
            sh = [k for k in hf if k in gkeys]
            cols[NPAIR] = sum(1 for k in sh if k[0] == 'V')
            cols[NPAIR + 1] = sum(1 for k in sh if k[0] == 'H')
            cols[NPAIR + 2] = sum(1 for k in sh if k[0] == 'C') / max(1, sum(1 for k in hf if k[0] == 'C'))
            for i, v in gcols:
                cols[NPAIR + 3 + i] = v
            ind.extend(cols.keys()); data.extend(cols.values()); ptr.append(len(ind))
        return hs, (data, ind, ptr)

    def matrix(self, parts):
        data, ind, ptr = [], [], [0]
        for d, i, p in parts:
            off = len(ind)
            data.extend(d); ind.extend(i); ptr.extend(off + x for x in p[1:])
        ncol = NPAIR + 3 + len(self.vocab.idx) + 1
        return sp.csr_matrix((np.array(data, dtype=np.float32), np.array(ind), np.array(ptr)),
                             shape=(len(ptr) - 1, ncol))

    def train(self, names, obj='binary', rounds=300):
        import lightgbm as lgb
        parts, ys, groups = [], [], []
        for n in names:
            own = set(self.knn.hints[n])
            hs, R = self.rows(n)
            if R is None:
                continue
            y = [1 if h in own else 0 for h in hs]
            if sum(y) == 0:
                continue
            parts.append(R); ys.extend(y); groups.append(len(hs))
        self.vocab.frozen = True
        X = self.matrix(parts)
        self.ncol = X.shape[1]
        params = dict(objective=obj, learning_rate=0.05, num_leaves=63, min_data_in_leaf=50,
                      feature_fraction=0.5, bagging_fraction=0.8, bagging_freq=1,
                      verbose=-1, num_threads=4)
        if obj == 'lambdarank':
            params['eval_at'] = [100]
            ds = lgb.Dataset(X, np.array(ys), group=groups)
        else:
            ds = lgb.Dataset(X, np.array(ys))
        self.model = lgb.train(params, ds, rounds)
        return X.shape, sum(ys)

    def scores(self, name):
        hs, R = self.rows(name)
        if R is None:
            return hs, np.zeros(0), None
        X = self.matrix([R])
        if X.shape[1] < self.ncol:
            X = sp.csr_matrix((X.data, X.indices, X.indptr), shape=(X.shape[0], self.ncol))
        return hs, self.model.predict(X), X

    def select(self, name, topn=100):
        hs, s, _ = self.scores(name)
        order = np.argsort(-s)
        return [(hs[i], float(s[i])) for i in order[:topn]]

    def save(self, path):
        m = self.model; self.model = None
        mstr = m.model_to_string()
        knn, base = self.knn, self.base
        self.knn = None; self.base = None
        pickle.dump((self, mstr), open(path, 'wb'))
        self.model, self.knn, self.base = m, knn, base

def load(path, knn):
    import lightgbm as lgb
    self, mstr = pickle.load(open(path, 'rb'))
    self.model = lgb.Booster(model_str=mstr)
    self.knn = knn; self.base = learnsel.Ranker(knn)
    return self

def split(names, seed, frac=3):
    origs = sorted(set(n.split('__goal_')[0] for n in names))
    random.seed(seed); random.shuffle(origs)
    test_o = set(origs[:max(1, len(origs) // frac)])
    train = [n for n in names if n.split('__goal_')[0] not in test_o]
    test = [n for n in names if n.split('__goal_')[0] in test_o]
    return train, test, test_o

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('hintdir')
    ap.add_argument('--obj', default='binary')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--ntrain', type=int, default=1500)
    ap.add_argument('--ntest', type=int, default=300)
    ap.add_argument('--rounds', type=int, default=300)
    ap.add_argument('--ncand', type=int, default=600)
    ap.add_argument('--save')
    ap.add_argument('--all', action='store_true', help='train on everything (for --save)')
    a = ap.parse_args()
    knn = hintsel.KNN(a.hintdir)
    names = [n for n in knn.hints if len(knn.hints[n]) >= 5]
    if a.all:
        train, test = names, []
    else:
        train, test, test_o = split(names, a.seed)
        print('test originals', sorted(test_o))
    random.seed(a.seed); random.shuffle(train); random.shuffle(test)
    rk = LGBRanker(knn, ncand=a.ncand)
    shape, npos = rk.train(train[:a.ntrain], a.obj, a.rounds)
    print('train matrix', shape, 'positives', npos)
    if a.save:
        rk.save(a.save)
    res = collections.defaultdict(list)
    for n in test[:a.ntest]:
        own = set(knn.hints[n])
        hs, s, X = rk.scores(n)
        if not hs:
            continue
        order = np.argsort(-s)
        for topn in (50, 100, 200):
            base = set(hs[:topn])
            lrn = set(hs[i] for i in order[:topn])
            res['knn%d' % topn].append(len(own & base) / len(own))
            res['lgb%d' % topn].append(len(own & lrn) / len(own))
            res['prec_knn%d' % topn].append(len(own & base) / max(1, len(base)))
            res['prec_lgb%d' % topn].append(len(own & lrn) / max(1, len(lrn)))
        res['cand'].append(len(own & set(hs)) / len(own))
    for k in sorted(res):
        print(f'{k}: {np.mean(res[k]):.3f}')
    if not test:
        return
    imp = rk.model.feature_importance('gain')
    inv = {NPAIR + 3 + i: k for k, i in rk.vocab.idx.items()}
    for i, k in enumerate(learnsel.FEATS + ['ovlV', 'ovlH', 'ovlC']):
        inv[i] = k
    top = np.argsort(-imp)[:25]
    print('top features:', ', '.join(f'{inv.get(i, i)}={imp[i]:.0f}' for i in top))

if __name__ == '__main__':
    main()
