"""A success model for the loop's fresh runs: logistic regression on binned features.

  python3 schedmodel.py eval FEATS.tsv [--test-frac 0.4]   # time split: last part of the last round
  python3 schedmodel.py train FEATS.tsv MODEL.json

FEATS.tsv comes from schedfeats.py. Each feature is cut at its quantiles (from
the training rows) into up to 8 bins, one-hot; the model is fitted by Newton's
method with an L2 penalty. score(x) is the predicted log-odds of THM.
"""
import argparse, json, math, sys
import numpy as np

NB = 8


def load(p):
    L = [l.rstrip('\n').split('\t') for l in open(p)]
    head = L[0][3:]
    rows = L[1:]
    meta = [(int(w[0]), w[1]) for w in rows]
    y = np.array([int(w[2]) for w in rows], float)
    X = np.array([[float(v) for v in w[3:]] for w in rows], float)
    return head, meta, X, y


# fixed bins for the distances in proof lines: quantile bins put everything beyond ~84 lines
# into one bin, and the scheduler then ran goals 700 lines away as if 100 (ABb: 6/132 vs 22
# predicted). Beyond 320 lines there are few runs to learn from (loop.py --sched-max-lgap).
D = [13.5, 21.5, 40.5, 80.5, 160.5, 320.5, 4999.5]
FIXED = {'lgap': D, 'agap': D, 'lg_new': [-0.5] + D}


def cuts(X, head=None):
    C = []
    for j in range(X.shape[1]):
        if head and head[j] in FIXED:
            C.append(list(FIXED[head[j]])); continue
        q = np.unique(np.quantile(X[:, j], np.linspace(0, 1, NB + 1)[1:-1]))
        C.append(q.tolist())
    return C


def onehot(X, C):
    cols = []
    for j, q in enumerate(C):
        b = np.searchsorted(np.array(q), X[:, j], side='right')
        M = np.zeros((X.shape[0], len(q) + 1))
        M[np.arange(X.shape[0]), b] = 1
        cols.append(M)
    return np.hstack([np.ones((X.shape[0], 1))] + cols)


def fit(Z, y, lam=1.0, it=30):
    w = np.zeros(Z.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (p - y) + lam * w
        H = (Z * (p * (1 - p))[:, None]).T @ Z + lam * np.eye(len(w))
        w -= np.linalg.solve(H, g)
    return w


def auc(s, y):
    o = np.argsort(s, kind='mergesort'); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    # ties: average ranks
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=r); r = (sums / cnt)[inv]
    P = y.sum(); N = len(y) - P
    return (r[y == 1].sum() - P * (P + 1) / 2) / (P * N)


def top(s, y, frac):
    k = max(1, int(len(s) * frac))
    o = np.argsort(-s, kind='mergesort')[:k]
    return y[o].mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('feats'); ap.add_argument('model', nargs='?')
    ap.add_argument('--test-frac', type=float, default=0.4)
    ap.add_argument('--lam', type=float, default=3.0)
    ap.add_argument('--drop', default='', help='features to leave out (comma-separated)')
    a = ap.parse_args()
    head, meta, X, y = load(a.feats)
    keep = [j for j, h in enumerate(head) if h not in a.drop.split(',')]
    head = [head[j] for j in keep]; X = X[:, keep]
    if a.cmd == 'eval':
        last = max(r for r, _ in meta)
        idx = [i for i, (r, _) in enumerate(meta) if r == last]
        cut = idx[int(len(idx) * (1 - a.test_frac))]
        tr = np.arange(cut); te = np.arange(cut, len(y))
        C = cuts(X[tr], head); w = fit(onehot(X[tr], C), y[tr], a.lam)
        s = onehot(X[te], C) @ w
        yt = y[te]
        print(f'train {len(tr)} ({y[tr].mean():.3f}), test {len(te)} ({yt.mean():.3f})')
        base = {'model': s, '-lgap': -X[te, head.index('lgap')] if 'lgap' in head else None}
        for nm, sc in base.items():
            if sc is None:
                continue
            print(f'  {nm:8s} AUC {auc(sc, yt):.3f}  top10% {top(sc, yt, .1):.3f}  top25% {top(sc, yt, .25):.3f}  top50% {top(sc, yt, .5):.3f}')
        # single-feature models
        for j, h in enumerate(head):
            Cj = [C[j]]; wj = fit(onehot(X[tr][:, [j]], Cj), y[tr], a.lam)
            sj = onehot(X[te][:, [j]], Cj) @ wj
            print(f'    only {h:10s} AUC {auc(sj, yt):.3f}  top25% {top(sj, yt, .25):.3f}')
    elif a.cmd == 'train':
        C = cuts(X, head); w = fit(onehot(X, C), y, a.lam)
        json.dump({'feats': head, 'cuts': C, 'w': w.tolist()}, open(a.model, 'w'))
        print(f'{len(y)} rows, {len(w)} weights -> {a.model}')


def train_rows(rows, feats, lam=3.0, recent=0):
    """a model from History.rows [(feature dict, label)]; with recent > 0, only the last rows"""
    if recent:
        rows = rows[-recent:]
    X = np.array([[x[h] for h in feats] for x, _ in rows], float)
    y = np.array([l for _, l in rows], float)
    C = cuts(X, list(feats)); w = fit(onehot(X, C), y, lam)
    return {'feats': list(feats), 'cuts': [np.array(q) for q in C], 'w': w}


def load_model(p):
    m = json.load(open(p))
    m['cuts'] = [np.array(q) for q in m['cuts']]
    m['w'] = np.array(m['w'])
    return m


def score(m, x):
    """x: dict feature -> value. Returns log-odds."""
    s = m['w'][0]; k = 1
    for h, q in zip(m['feats'], m['cuts']):
        b = int(np.searchsorted(q, x[h], side='right'))
        s += m['w'][k + b]; k += len(q) + 1
    return float(s)


if __name__ == '__main__':
    main()
