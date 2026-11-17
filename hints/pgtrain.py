#!/usr/bin/env python3
"""Train the parental model (17 Nov): LightGBM on pgdata.py rows; evaluate on held-out runs with all pairs.

usage: pgtrain.py TRAIN.npz TEST.npz OUT [trees leaves]
The model is additive (interaction constraints: each tree on the new rule's features 0-9 or on the partner's
10-19; the id gap, column 20, is not used), so twee scores each rule once (splitPGModel, pgParts).
Writes OUT.txt (LightGBM) and OUT.bin (twee, lgb2bin.py). Prints, for thresholds on the predicted
probability, the share of generated overlaps (weighted) kept and the share of proof-parent pairs kept, and the
same for the sum-of-scores filter (sigmoid(q1 + q2), twee's --pg-threshold without --pg-model).
"""
import sys, subprocess, os
import numpy as np, lightgbm as lgb

args = sys.argv[1:]
drop = []   # --drop ps,id: zero these per-rule features in training (in both roles), so no tree uses them
if '--drop' in args:
    i = args.index('--drop'); drop = args[i + 1].split(','); del args[i:i + 2]
sys.argv[1:] = args
tr, te, out = sys.argv[1:4]
trees = int(sys.argv[4]) if len(sys.argv) > 4 else 100
leaves = int(sys.argv[5]) if len(sys.argv) > 5 else 31
A = np.load(tr); B = np.load(te)
names = ['%s_%s' % (b, f) for b in ('r', 'a') for f in ('q', 'lsz', 'rsz', 'nv', 'dep', 'hint', 'ori', 'id', 'ps', 'nact')]
FN = ('q', 'lsz', 'rsz', 'nv', 'dep', 'hint', 'ori', 'id', 'ps', 'nact')
XA = A['X'][:, :20].copy()
for f in drop:
    XA[:, FN.index(f)] = 0; XA[:, 10 + FN.index(f)] = 0
d = lgb.Dataset(XA, A['y'], feature_name=names, free_raw_data=False)
m = lgb.train({'objective': 'binary', 'num_leaves': leaves, 'learning_rate': 0.1, 'min_data_in_leaf': 50,
               'feature_fraction': 0.9, 'bagging_fraction': 0.8, 'bagging_freq': 1, 'verbose': -1, 'num_threads': 4,
               'interaction_constraints': [list(range(10)), list(range(10, 20))]},
              d, num_boost_round=trees)
m.save_model(out + '.txt')
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lgb2bin.py'), out + '.txt', out + '.bin'], check=True)
X, y, n = B['X'], B['y'], B['n'].astype(np.float64)
p = m.predict(X[:, :20])
q = 1 / (1 + np.exp(-(X[:, 0].astype(np.float64) + X[:, 10])))
print('train %d rows (%d pos), test %d rows (%d pos), %d overlaps' % (len(A['y']), A['y'].sum(), len(y), y.sum(), n.sum()))
for name, s in (('model', p), ('sum', q)):
    for t in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8):
        k = s >= t
        print('%-5s %.2f: overlaps kept %5.1f%%  pairs kept %5.1f%%  proof pairs kept %5.1f%%' %
              (name, t, 100 * n[k].sum() / n.sum(), 100 * k.mean(), 100 * k[y == 1].mean()))
imp = sorted(zip(m.feature_importance('gain'), names), reverse=True)
print('gain:', ', '.join('%s %.0f' % (b, a) for a, b in imp[:12]))
