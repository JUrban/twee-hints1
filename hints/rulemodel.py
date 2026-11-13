#!/usr/bin/env python3
"""ENIGMA for twee: learn which added rules end up in the proof.

Data: given.py output (label, index, lhs, rhs per added rule).
Row = enigmatic features of the rule ('c:' block) + of the goal ('g:')
+ overlap counts + log(rule index).

rulemodel.py GIVENDIR [--save MODEL.txt --vocab VOCAB.tsv] [--all]
Evaluation (held-out originals): AUC, and for thresholds the share of
positive rules kept, negative rules rejected, and the proof's last
positive position among the kept rules relative to the unfiltered run.
"""
import argparse, collections, math, os, random, sys
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enigfeats, hintsel

NFIX = 4  # ovlV, ovlH, ovlC, logidx

def load(path, parents=False):
    """Rows (label, idx, lhs, rhs); with parents=True also the parents'
    equations as a fifth element (list of (lhs, rhs))."""
    rows = []; byidx = {}; par = []
    for line in open(path):
        f = line.rstrip('\n').split('\t')
        lab, idx, l, r = int(f[0]), int(f[1]), f[2], f[3]
        byidx[idx] = (l, r)
        rows.append((lab, idx, l, r))
        par.append((int(f[4]), int(f[5])) if len(f) >= 6 else (0, 0))
    if not parents:
        return rows
    return [x + ([byidx[p - 1] for p in ps if p > 0 and p - 1 in byidx],) for x, ps in zip(rows, par)]

THEORY = False  # add the 't:' block: features summed over the problem's axioms (ENIGMA's theory block)

def goal_feats(name):
    """Per-problem constant features: the goal block, and with THEORY the
    theory block (keys prefixed 'T', so they become 'g:T...' columns)."""
    f = collections.Counter()
    lits = hintsel.goal_lits(name)
    for pos, l, r in lits:
        for k, v in enigfeats.features(l, r).items():
            f[('' if pos else 'n') + k] += v
    f['Llits'] = len(lits)
    if THEORY:
        import given
        axs = given.axioms(name)
        for l, r in axs:
            for k, v in enigfeats.features(l, r).items():
                if k[0] in 'VHC':
                    f['T' + k] += v
        f['TLaxioms'] = len(axs)
    return f

class RuleModel:
    def __init__(self, parents=False):
        self.vocab = enigfeats.Vocab()
        self.model = None
        self.parents = parents

    def rows(self, name, items):
        """items: list of (idx, lhs, rhs[, parents]). Returns CSR parts."""
        g = goal_feats(name)
        gcols = [(self.vocab.get('g:' + k), v) for k, v in g.items()]
        gcols = [(i, v) for i, v in gcols if i is not None]
        gkeys = set(k for k in g if k[0] in 'VHC')
        data, ind, ptr = [], [], [0]
        for it in items:
            idx, l, r = it[:3]
            hf = enigfeats.features(l, r)
            cols = {}
            if self.parents and len(it) > 3:
                pf = collections.Counter()
                for pl, pr in it[3]:
                    pf.update(enigfeats.features(pl, pr))
                for k, v in pf.items():
                    i = self.vocab.get('p:' + k)
                    if i is not None:
                        cols[NFIX + i] = v
            sh = [k for k in hf if k in gkeys]
            cols[0] = sum(1 for k in sh if k[0] == 'V')
            cols[1] = sum(1 for k in sh if k[0] == 'H')
            cols[2] = sum(1 for k in sh if k[0] == 'C') / max(1, sum(1 for k in hf if k[0] == 'C'))
            cols[3] = math.log(1 + idx)
            for k, v in hf.items():
                i = self.vocab.get('c:' + k)
                if i is not None:
                    cols[NFIX + i] = v
            for i, v in gcols:
                cols[NFIX + i] = v
            ind.extend(cols.keys()); data.extend(cols.values()); ptr.append(len(ind))
        return data, ind, ptr

    def matrix(self, parts, ncol=None):
        data, ind, ptr = [], [], [0]
        for d, i, p in parts:
            off = len(ind)
            data.extend(d); ind.extend(i); ptr.extend(off + x for x in p[1:])
        ncol = ncol or NFIX + len(self.vocab.idx) + 1
        return sp.csr_matrix((np.array(data, dtype=np.float32), np.array(ind, dtype=np.int64),
                              np.array(ptr, dtype=np.int64)), shape=(len(ptr) - 1, ncol))

    def train(self, givendir, names, negmax=400, rounds=200, leaves=63, seed=1, threads=8):
        """givendir: a directory, or a dict name -> path."""
        import lightgbm as lgb
        rnd = random.Random(seed)
        parts, ys = [], []
        for n in names:
            path = givendir[n] if isinstance(givendir, dict) else os.path.join(givendir, n)
            rows = [x for x in load(path, self.parents) if x[0] >= 0]
            pos = [x for x in rows if x[0] == 1]
            neg = [x for x in rows if x[0] == 0]
            if not pos:
                continue
            if len(neg) > negmax:
                neg = rnd.sample(neg, negmax)
            sel = pos + neg
            parts.append(self.rows(n, [x[1:] for x in sel]))
            ys.extend(x[0] for x in sel)
        self.vocab.frozen = True
        X = self.matrix(parts)
        self.ncol = X.shape[1]
        y = np.array(ys)
        params = dict(objective='binary', learning_rate=0.1, num_leaves=leaves,
                      min_data_in_leaf=20, feature_fraction=0.5, bagging_fraction=0.8,
                      bagging_freq=1, verbose=-1, num_threads=threads,
                      scale_pos_weight=float((y == 0).sum()) / max(1, (y == 1).sum()))
        self.model = lgb.train(params, lgb.Dataset(X, y), rounds)
        return X.shape, int(y.sum())

    def predict(self, name, items):
        X = self.matrix([self.rows(name, items)], self.ncol)
        return self.model.predict(X)

    def save(self, model_path, vocab_path):
        self.model.save_model(model_path)
        with open(vocab_path, 'w') as f:
            for k, i in sorted(self.vocab.idx.items(), key=lambda x: x[1]):
                f.write(f'{NFIX + i}\t{k}\n')

def auc(y, s):
    order = np.argsort(s)
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    npos = y.sum(); nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return None
    return (ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('givendir')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--ntest', type=int, default=300)
    ap.add_argument('--rounds', type=int, default=200)
    ap.add_argument('--leaves', type=int, default=63)
    ap.add_argument('--negmax', type=int, default=400)
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--theory', action='store_true', help='add the theory block (axiom features)')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--parents', action='store_true', help='add the parents\' features (p: block)')
    ap.add_argument('--test-origs', help='comma-separated originals to hold out')
    ap.add_argument('--save'); ap.add_argument('--vocab')
    a = ap.parse_args()
    global THEORY
    THEORY = a.theory
    paths = {}
    for d in a.givendir.split(','):
        if os.path.isdir(d):
            for n in os.listdir(d):
                paths[n] = os.path.join(d, n)
    names = sorted(paths)
    origs = sorted(set(n.split('__goal_')[0] for n in names))
    random.seed(a.seed); random.shuffle(origs)
    test_o = set() if a.all else set(origs[:max(1, len(origs) // 3)])
    if a.test_origs:
        test_o = set(a.test_origs.split(','))
    train = [n for n in names if n.split('__goal_')[0] not in test_o]
    test = [n for n in names if n.split('__goal_')[0] in test_o]
    print('test originals', sorted(test_o))
    m = RuleModel(a.parents)
    print('train', m.train(paths, train, a.negmax, a.rounds, a.leaves, a.seed, a.threads))
    if a.save:
        m.save(a.save, a.vocab or a.save + '.vocab')
    random.shuffle(test)
    aucs = []; stats = collections.defaultdict(list)
    for n in test[:a.ntest]:
        rows = [x for x in load(paths[n], a.parents) if x[0] >= 0]
        if len(rows) < 20 or not any(x[0] == 1 for x in rows):
            continue
        y = np.array([x[0] for x in rows]); s = m.predict(n, [x[1:] for x in rows])
        v = auc(y, s)
        if v is not None:
            aucs.append(v)
        last = max(i for i, x in enumerate(rows) if x[0] == 1) + 1
        for t in (0.05, 0.1, 0.2, 0.3, 0.5):
            keep = s >= t
            stats[t].append((keep[y == 1].mean(), 1 - keep[y == 0].mean(),
                             keep[:last].sum() / last))
    print(f'AUC {np.mean(aucs):.3f} over {len(aucs)} problems')
    for t, L in sorted(stats.items()):
        A = np.array(L)
        print(f'threshold {t}: positives kept {A[:,0].mean():.3f}, negatives rejected {A[:,1].mean():.3f}, '
              f'rules until proof kept {A[:,2].mean():.3f}, all-pos-kept {np.mean(A[:,0] == 1):.2f}')


def write_goalfile(name, vocab, path):
    """Goal block of the rule model for twee --rule-goal."""
    g = goal_feats(name)
    with open(path, 'w') as f:
        for k, v in g.items():
            c = vocab.get('g:' + k)
            if c is not None:
                f.write(f'{c}\t{v}\n')
        for k in g:
            if k[0] in 'VHC':
                f.write(f'K\t{k}\n')

def goalfiles_main(argv):
    global THEORY
    if '--theory' in argv:
        THEORY = True
        argv = [x for x in argv if x != '--theory']
    vocab_path, names_path, outdir = argv
    vocab = {}
    for line in open(vocab_path):
        c, k = line.rstrip('\n').split('\t')
        vocab[k] = int(c)
    os.makedirs(outdir, exist_ok=True)
    for n in open(names_path):
        n = n.split()[0]
        write_goalfile(n, vocab, os.path.join(outdir, n))

if __name__ == '__main__':
    if sys.argv[1:2] == ['goalfiles']:
        goalfiles_main(sys.argv[2:])
    else:
        main()
