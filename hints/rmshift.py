#!/usr/bin/env python3
"""(19 Nov, exp37) Calibration shift of a rule model: add DELTA to every leaf of its first tree, so every raw score
moves by DELTA, the ranking (AUC) stays, and the thresholds production tuned for rm4t (deferral at 0.1, parental
guidance at q1 + q2 >= logit 0.25) prune as much as with rm4t. DELTA makes the model defer, at 0.1, the same share of
the rules in the given logs NAMES as the reference model. The labels are not used.

rmshift.py MODEL REF NAMES GIVENDIR OUT [--n 100]     (MODEL, REF, OUT: path stems of .txt/.vocab; OUT.bin written)
"""
import math, os, random, shutil, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rulemodel as R

def load(stem):
    import lightgbm as lgb
    m = R.RuleModel()
    for line in open(stem + '.vocab'):
        i, k = line.rstrip('\n').split('\t', 1)
        m.vocab.idx[k] = int(i) - R.NFIX
    m.vocab.frozen = True
    m.model = lgb.Booster(model_file=stem + '.txt')
    m.ncol = m.model.num_feature()
    return m

def raws(m, names, gd):
    out = []
    for n in names:
        rows = [x for x in R.load(os.path.join(gd, n)) if x[0] >= 0]
        X = m.matrix([m.rows(n, [x[1:] for x in rows])], m.ncol)
        out.append(m.model.predict(X, raw_score=True))
    return out

def share(rs, d, t=0.1):
    lt = math.log(t / (1 - t))
    return float(np.mean([np.mean(r + d < lt) for r in rs]))

def main():
    a = sys.argv[1:]
    n = int(a[a.index('--n') + 1]) if '--n' in a else 100
    stem, ref, names, gd, out = a[:5]
    R.THEORY = True
    ns = sorted(open(names).read().split())
    random.Random(1).shuffle(ns); ns = ns[:n]
    target = share(raws(load(ref), ns, gd), 0.0)
    rs = raws(load(stem), ns, gd)
    lo, hi = -10.0, 10.0   # (share falls as DELTA grows)
    for _ in range(60):
        mid = (lo + hi) / 2
        if share(rs, mid) > target:
            lo = mid
        else:
            hi = mid
    d = (lo + hi) / 2
    print(f'reference defers {target:.3f}; model {share(rs, 0.0):.3f} unshifted; DELTA {d:+.4f} -> {share(rs, d):.3f}',
          flush=True)
    txt = open(stem + '.txt').read().split('\n')
    k = txt.index('Tree=0')
    for j in range(k, len(txt)):
        if txt[j].startswith('leaf_value='):
            txt[j] = 'leaf_value=' + ' '.join(repr(float(v) + d) for v in txt[j][len('leaf_value='):].split())
            break
    txt = [l for l in txt if not l.startswith('tree_sizes=')]   # (byte sizes of the trees; LightGBM then parses in order)
    open(out + '.txt', 'w').write('\n'.join(txt))
    shutil.copy(stem + '.vocab', out + '.vocab')
    subprocess.check_call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lgb2bin.py'),
                           out + '.txt', out + '.bin'])
    chk = raws(load(out), ns[:5], gd); orig = raws(load(stem), ns[:5], gd)
    print('check: raw shift on 5 logs', float(np.mean(np.concatenate(chk) - np.concatenate(orig))), flush=True)

if __name__ == '__main__':
    main()
