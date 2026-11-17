#!/usr/bin/env python3
"""Train a Pcat parental model on ENIGMA features (17 Nov; FroCoS 2021): LightGBM on pgdata_enigma.py rows.

usage: pgtrain_enigma.py TRAIN TEST OUT [--trees T] [--leaves L] [--enigma-only] [--additive]
TRAIN/TEST are pgdata_enigma.py outputs (without .npz). --enigma-only: only the two ENIGMA vectors (as the
paper), not the 10 per-rule features and the id gap. Writes OUT.txt and OUT.bin (twee --pg-model with
--pg-enigma), prints the share of overlaps and of proof pairs kept by threshold, and the threshold at which
the model keeps as many overlaps as the sum filter at 0.269.
--additive: interaction constraints, so that each tree uses only the new rule's side (its ENIGMA vector and its
10 features) or only the partner's; twee (splitPGModelE) then scores each rule once in both roles and a pair
costs two lookups, where a full forest costs ~30 us per judged pair. The id gap is left out.
"""
import sys, os, subprocess
import numpy as np, scipy.sparse as sp, lightgbm as lgb

a = sys.argv[1:]
def opt(name, default):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return type(default)(v)
    return default
trees = opt('--trees', 100); leaves = opt('--leaves', 255)
eo = '--enigma-only' in a
if eo:
    a.remove('--enigma-only')
add = '--additive' in a
if add:
    a.remove('--additive')
tr, te, out = a[:3]
def load(p):
    Z = np.load(p + '.npz'); X = sp.load_npz(p + '.X.npz').tocsr()
    return X, Z['y'], Z['n'].astype(np.float64), int(Z['C'])
X, y, _, C = load(tr)
Xt, yt, nt, _ = load(te)
if eo:
    X = X[:, :2 * C]; Xt = Xt[:, :2 * C]
elif add:
    X = X[:, :2 * C + 20]; Xt = Xt[:, :2 * C + 20]
par = {'objective': 'binary', 'num_leaves': leaves, 'learning_rate': 0.1, 'min_data_in_leaf': 20,
       'feature_fraction': 0.9, 'bagging_fraction': 0.8, 'bagging_freq': 1, 'verbose': -1, 'num_threads': 4}
if add:
    side_r = list(range(C)) + ([] if eo else list(range(2 * C, 2 * C + 10)))
    side_a = list(range(C, 2 * C)) + ([] if eo else list(range(2 * C + 10, 2 * C + 20)))
    par['interaction_constraints'] = [side_r, side_a]
m = lgb.train(par, lgb.Dataset(X, y), num_boost_round=trees)
m.save_model(out + '.txt')
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lgb2bin.py'), out + '.txt', out + '.bin'], check=True)
p = m.predict(Xt)
print('train %d rows (%d pos), test %d rows (%d pos), %d columns' % (len(y), y.sum(), len(yt), yt.sum(), X.shape[1]))
for t in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5):
    k = p >= t
    print('%.3f: overlaps kept %5.1f%%  proof pairs kept %5.1f%%' % (t, 100 * nt[k].sum() / nt.sum(), 100 * k[yt == 1].mean()))
# the sum filter's share at 0.269, from the per-rule raw scores (column 2C and 2C+10)
D = Xt[:, 2 * C:2 * C + 21].toarray() if not eo else sp.load_npz(te + '.X.npz').tocsr()[:, 2 * C:2 * C + 21].toarray()
q = 1 / (1 + np.exp(-(D[:, 0].astype(np.float64) + D[:, 10])))
target = nt[q >= 0.269].sum() / nt.sum()
o = np.argsort(-p); cum = np.cumsum(nt[o]) / nt.sum(); t = p[o][min(np.searchsorted(cum, target), len(o) - 1)]
print('sum 0.269 keeps %.1f%% overlaps, %.1f%% proof pairs; model at %.4f keeps %.1f%%, %.1f%% proof pairs' %
      (100 * target, 100 * (q >= 0.269)[yt == 1].mean(), t, 100 * nt[p >= t].sum() / nt.sum(), 100 * (p >= t)[yt == 1].mean()))
