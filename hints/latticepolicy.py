#!/usr/bin/env python3
"""A policy over the climb's lattice moves (15 Nov; the user: learn the up/down steps, randomized guidance).

  latticepolicy.py train ROWS.tsv --out policy.json [--label nontrivial|credit] [--test-frac 0.25]

Logistic regression (numpy, L2, standardised features) on latticedata.py rows; the label is
'nontrivial' (the sketch was proved, used an assumption, and has >= 30 steps), 'credit' (> 0: the
target's real proof reused the sketch's steps) or 'realized' (soft: the share of the sketch's steps
that the real final run derived, 0 for a failed sketch). The held-out split is by target, so moves of one
target are never on both sides. climb.py --move-model scores the queued moves with it and samples
the next by softmax (--move-temp), with --move-eps random moves.
"""
import argparse, csv, json, math, os, random, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latticedata import FEATURES


def load(path, label):
    X, y, g = [], [], []
    for r in csv.DictReader(open(path), delimiter='\t'):
        if label == 'realized':
            # soft label: the share of the sketch's steps the real final run derived; 0 for a failed sketch
            if r['proved'] == '1' and not r['realized']:
                continue
            v = float(r['realized']) if r['proved'] == '1' else 0.0
        elif label == 'credit':
            if r['proved'] != '1' or not r['credit']:
                continue
            v = float(r['credit']) > 0.05
        else:
            if r['nontrivial'] == '':
                continue
            v = r['nontrivial'] == '1'
        X.append([float(r[k]) for k in FEATURES]); y.append(float(v)); g.append(r['target'])
    return np.array(X), np.array(y), g


def fit(X, y, l2=1.0, iters=3000, lr=0.1):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    w = np.zeros(Z.shape[1]); b = math.log((y.mean() + 1e-3) / (1 - y.mean() + 1e-3))
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w + b)))
        w -= lr * (Z.T @ (p - y) / len(y) + l2 * w / len(y))
        b -= lr * (p - y).mean()
    return {'features': FEATURES, 'mu': mu.tolist(), 'sd': sd.tolist(), 'w': w.tolist(), 'b': float(b)}


def score(m, x):
    return sum(wi * (xi - mi) / si for wi, xi, mi, si in zip(m['w'], x, m['mu'], m['sd'])) + m['b']


def auc(s, y):
    pos = [a for a, b in zip(s, y) if b]; neg = [a for a, b in zip(s, y) if not b]
    if not pos or not neg:
        return float('nan')
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['train'])
    ap.add_argument('rows'); ap.add_argument('--out', required=True)
    ap.add_argument('--label', default='nontrivial', choices=['nontrivial', 'credit', 'realized'])
    ap.add_argument('--test-frac', type=float, default=0.25)
    ap.add_argument('--l2', type=float, default=1.0)
    a = ap.parse_args()
    X, y, g = load(a.rows, a.label)
    ts = sorted(set(g)); random.Random(7).shuffle(ts)
    test = set(ts[:int(len(ts) * a.test_frac)])
    tr = np.array([t not in test for t in g])
    m = fit(X[tr], y[tr], a.l2)
    s_te = [score(m, x) for x in X[~tr]]
    yb = y[~tr] > (0.5 if a.label != 'realized' else np.median(y[y > 0]) if (y > 0).any() else 0.5)
    print(f'{len(y)} moves (mean label {y.mean():.3f}), {len(ts)} targets; held-out {(~tr).sum()} moves of {len(test)} '
          f'targets: AUC {auc(s_te, yb):.3f}' + (' (label above the median of positive)' if a.label == 'realized' else ''))
    m = fit(X, y, a.l2)   # the saved model uses all rows
    m['label'] = a.label; m['n'] = int(len(y))
    for k, w in sorted(zip(FEATURES, m['w']), key=lambda x: -abs(x[1])):
        print(f'  {k:12s} {w:+.3f}')
    json.dump(m, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
