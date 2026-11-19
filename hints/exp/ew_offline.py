#!/usr/bin/env python3
"""ENIGMAWatch offline test (exp31; notes/2026-11-19-enigmawatch.md).

Goertzel, Jakubuv, Urban, ENIGMAWatch: ProofWatch Meets ENIGMA (TABLEAUX 2019), section 3, for twee's rule model:
* watchlists: proofs of proven goals of the TRAINING originals (loops/UL/hints/<goal>, one watchlist per goal);
* a rule matches a watchlist step if their canonical keys are equal (variables renamed by first occurrence, the
  smaller orientation): an under-approximation of ProofWatch's subsumption;
* completion c_W(t) = matched steps of W among the rules before t / |W|; the proof-state vector is c over a fixed
  set of 512 watchlists;
* selection (3.2): M = per problem, the mean of c over its rules; Mean = the 512 columns of highest mean (also Var,
  Rand);
* rows = rulemodel.py's (rm4t: theory block) plus the 512 ratios; two LightGBM models on the same rows, with and
  without them; evaluation on held-out originals (no watchlist comes from them): per-problem AUC, paired.

ew_offline.py GIVENDIR HINTSDIR OUT [--ntrain 1500 --ntest 300 --nsel 800 --k 512 --sel mean|var|rand --negmax 200]
"""
import argparse, collections, json, math, os, random, re, sys, time
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, '/project/twee/hints')
import rulemodel

VAR_RE = re.compile(r'X\d+')

def ren(s):
    m = {}
    return VAR_RE.sub(lambda x: m.setdefault(x.group(), 'X%d' % len(m)), s)

def key(l, r):
    return min(ren(l + '=' + r), ren(r + '=' + l))

def orig(n):
    return n.split('__goal_')[0]

def read_log(path):
    """[(label, idx, lhs, rhs, key)] in file (addition) order"""
    out = []
    for line in open(path):
        f = line.rstrip('\n').split('\t')
        if len(f) < 4:
            continue
        out.append((int(f[0]), int(f[1]), f[2], f[3], key(f[2], f[3])))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('givendir'); ap.add_argument('hintsdir'); ap.add_argument('out')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--ntrain', type=int, default=1500)
    ap.add_argument('--ntest', type=int, default=300)
    ap.add_argument('--nsel', type=int, default=800, help='training problems for the selection matrix M')
    ap.add_argument('--k', type=int, default=512)
    ap.add_argument('--sel', default='mean,var,rand')
    ap.add_argument('--negmax', type=int, default=200)
    ap.add_argument('--rounds', type=int, default=200)
    ap.add_argument('--threads', type=int, default=2)
    a = ap.parse_args()
    rulemodel.THEORY = True
    t0 = time.time()
    def log(*x):
        print(f'[{time.time() - t0:7.1f}s]', *x, flush=True)
    names = sorted(os.listdir(a.givendir))
    origs = sorted(set(map(orig, names)))
    random.seed(a.seed); random.shuffle(origs)
    test_o = set(origs[:len(origs) // 3])        # as rulemodel.py's default split
    rnd = random.Random(a.seed)
    trn = [n for n in names if orig(n) not in test_o]; tst = [n for n in names if orig(n) in test_o]
    rnd.shuffle(trn); rnd.shuffle(tst)
    trn = trn[:a.ntrain]; tst = tst[:a.ntest]
    log('originals', len(origs), 'test originals', len(test_o), 'train', len(trn), 'test', len(tst))
    # watchlists: proofs of the training originals' proven goals
    W = []; wname = []
    for n in sorted(os.listdir(a.hintsdir)):
        if orig(n) in test_o:
            continue
        ks = set()
        for line in open(os.path.join(a.hintsdir, n)):
            f = line.rstrip('\n').split('\t')
            if len(f) >= 2:
                ks.add(key(f[0], f[1]))
        if ks:
            W.append(ks); wname.append(n)
    inv = collections.defaultdict(list)
    for i, ks in enumerate(W):
        for k in ks:
            inv[k].append(i)
    inv = {k: np.array(v, dtype=np.int64) for k, v in inv.items()}
    wsize = np.array([len(ks) for ks in W], dtype=np.float64)
    widx = {n: i for i, n in enumerate(wname)}
    log('watchlists', len(W), 'distinct steps', len(inv), 'median size', int(np.median(wsize)))
    # selection matrix M: mean completion over each sampled training run
    logs = {}
    def getlog(n):
        if n not in logs:
            logs[n] = read_log(os.path.join(a.givendir, n))
        return logs[n]
    selp = trn[:a.nsel]
    M = np.zeros((len(selp), len(W)), dtype=np.float32)
    for r, n in enumerate(selp):
        L = getlog(n); T = len(L); seen = set()
        acc = collections.defaultdict(float)
        for p, x in enumerate(L):
            k = x[4]
            if k in seen:
                continue
            seen.add(k)
            for i in inv.get(k, ()):
                acc[i] += (T - p - 1) / T     # matched before rules p+1..T-1
        for i, v in acc.items():
            M[r, i] = v / wsize[i]
        if r % 100 == 0:
            log('M row', r)
        own = widx.get(n)
        if own is not None:
            M[r, own] = 0.0
    log('M built', M.shape, 'nonzero share %.3f' % (M > 0).mean())
    sels = {}
    for s in a.sel.split(','):
        if s == 'mean':
            sels[s] = list(np.argsort(-M.mean(0))[:a.k])
        elif s == 'var':
            sels[s] = list(np.argsort(-M.var(0))[:a.k])
        elif s == 'rand':
            sels[s] = random.Random(a.seed + 7).sample(range(len(W)), a.k)
    w2j = {}
    for s, S in sels.items():
        w2j[s] = np.full(len(W), -1, dtype=np.int64); w2j[s][np.array(S)] = np.arange(len(S))
    ssize = {s: wsize[np.array(S)].astype(np.float32) for s, S in sels.items()}
    for s, S in sels.items():
        log(s, 'selected: mean completion %.4f, median size %d, originals %d' % (
            M[:, S].mean(), int(np.median(wsize[S])), len(set(orig(wname[i]) for i in S))))
    # rows
    m = rulemodel.RuleModel()
    def problem_rows(n, train):
        """base CSR parts, labels, and per selection the completion rows (list of dicts col -> value)"""
        L = getlog(n)
        lab = [(p, x) for p, x in enumerate(L) if x[0] >= 0]
        if train:
            pos = [z for z in lab if z[1][0] == 1]; neg = [z for z in lab if z[1][0] == 0]
            if not pos:
                return None
            if len(neg) > a.negmax:
                neg = rnd.sample(neg, a.negmax)
            lab = sorted(pos + neg)
        want = set(p for p, _ in lab)
        own = widx.get(n)
        cnt = {s: np.zeros(a.k, dtype=np.float32) for s in sels}
        ew = {s: np.zeros((len(lab), a.k), dtype=np.float32) for s in sels}
        seen = set(); r = 0
        for p, x in enumerate(L):
            if p in want:
                for s in sels:
                    ew[s][r] = cnt[s] / ssize[s]
                r += 1
            k = x[4]
            if k in seen:
                continue
            seen.add(k)
            ii = inv.get(k)
            if ii is None:
                continue
            if own is not None:
                ii = ii[ii != own]   # the problem's own proof is never a feature
            for s in sels:
                j = w2j[s][ii]; j = j[j >= 0]
                if len(j):
                    cnt[s][j] += 1   # (a watchlist holds each key once, so j has no repeats)
        base = m.rows(n, [x[1:4] for _, x in lab])
        return base, np.array([x[0] for _, x in lab]), ew
    def ewmat(rows, k):
        return sp.csr_matrix(rows if isinstance(rows, np.ndarray) else np.vstack(rows))
    parts, ys, ewr = [], [], {s: [] for s in sels}
    for n in trn:
        z = problem_rows(n, True)
        if z is None:
            continue
        parts.append(z[0]); ys.append(z[1])
        for s in sels:
            ewr[s].append(z[2][s])
        logs.pop(n, None)
        if len(parts) % 200 == 0:
            log('train problems', len(parts))
    m.vocab.frozen = True
    Xb = m.matrix(parts); y = np.concatenate(ys); ncol = Xb.shape[1]
    nnz = {s: float(np.mean([(d > 0).sum(1).mean() for d in ewr[s]])) for s in sels}
    log('train rows', Xb.shape, 'positives', int(y.sum()), 'completion nonzeros per row', {s: round(v, 1) for s, v in nnz.items()})
    import lightgbm as lgb
    params = dict(objective='binary', learning_rate=0.1, num_leaves=63, min_data_in_leaf=20, feature_fraction=0.5,
                  bagging_fraction=0.8, bagging_freq=1, verbose=-1, num_threads=a.threads, seed=a.seed,
                  scale_pos_weight=float((y == 0).sum()) / max(1, (y == 1).sum()))
    models = {'base': lgb.train(params, lgb.Dataset(Xb, y), a.rounds)}
    log('trained base')
    for s in sels:
        X = sp.hstack([Xb, ewmat(ewr[s], a.k)], format='csr'); ewr[s] = None
        models[s] = lgb.train(params, lgb.Dataset(X, y), a.rounds); del X
        imp = models[s].feature_importance('gain'); spl = models[s].feature_importance('split')
        log('trained', s, 'watchlist features used %d of %d, gain share %.3f, split share %.3f' % (
            int((spl[ncol:] > 0).sum()), a.k, imp[ncol:].sum() / imp.sum(), spl[ncol:].sum() / spl.sum()))
    del ewr
    # evaluation on the held-out originals
    res = []
    for n in tst:
        z = problem_rows(n, False)
        logs.pop(n, None)
        if z is None:
            continue
        base, yt, ew = z
        if len(yt) < 20 or yt.sum() == 0 or yt.sum() == len(yt):
            continue
        Xt = m.matrix([base], ncol)
        sc = {'base': models['base'].predict(Xt)}
        for s in sels:
            sc[s] = models[s].predict(sp.hstack([Xt, ewmat(ew[s], a.k)], format='csr'))
        row = {'name': n, 'n': int(len(yt)), 'pos': int(yt.sum())}
        for arm, v in sc.items():
            row['auc_' + arm] = float(rulemodel.auc(yt, v))
            for t in (0.1, 0.2):
                keep = v >= t
                row[f'kp{t}_{arm}'] = float(keep[yt == 1].mean()); row[f'rn{t}_{arm}'] = float(1 - keep[yt == 0].mean())
        res.append(row)
    with open(a.out, 'w') as f:
        for r in res:
            f.write(json.dumps(r) + '\n')
    log('test problems', len(res))
    for arm in ['base'] + list(sels):
        A = np.array([r['auc_' + arm] for r in res])
        line = f'{arm:5s} AUC mean {A.mean():.4f} median {np.median(A):.4f}'
        for t in (0.1, 0.2):
            kp = np.mean([r[f'kp{t}_{arm}'] for r in res]); rn = np.mean([r[f'rn{t}_{arm}'] for r in res])
            line += f' | t={t}: pos kept {kp:.4f} neg rejected {rn:.4f}'
        if arm != 'base':
            d = A - np.array([r['auc_base'] for r in res])
            line += f' | paired dAUC {d.mean():+.4f} (better {int((d > 0).sum())}, worse {int((d < 0).sum())})'
        print(line, flush=True)

if __name__ == '__main__':
    main()
