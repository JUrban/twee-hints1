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

def goal_feats(name, lits=None):
    """Per-problem constant features: the goal block, and with THEORY the
    theory block (keys prefixed 'T', so they become 'g:T...' columns).
    LITS: (positive, lhs, rhs) of another goal over NAME's axioms (a cut)."""
    f = collections.Counter()
    lits = hintsel.goal_lits(name) if lits is None else lits
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

_W = None   # (the model whose frozen vocab forked feature workers use)

def _log_part(args):
    """One log's rows for train(): (CSR part, labels, (positives, negatives)) or None."""
    n, path, negmax, negratio, seed = args
    m = _W
    rnd = random.Random(f'{seed}:{n}')
    rows = [x for x in load(path, m.parents) if x[0] >= 0]
    pos = [x for x in rows if x[0] == 1]
    neg = [x for x in rows if x[0] == 0]
    if not pos:
        return None
    k = max(negmax, int(round(negratio * len(pos)))) if negratio > 0 else negmax
    if len(neg) > k:
        neg = rnd.sample(neg, k)
    sel = pos + neg
    part = m.rows(n.split('@')[0], [x[1:] for x in sel])   # (NAME@K: K-th proof of NAME, --list)
    part = tuple(np.asarray(z, t) for z, t in zip(part, (np.float32, np.int32, np.int64)))
    return part, np.array([x[0] for x in sel], dtype=np.int8), (len(pos), len(neg))

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
        # (19 Nov) numpy parts: Python lists of all rows took 34 GB for rm7t
        datas, inds, ptrs = [], [], [np.zeros(1, np.int64)]
        off = 0; nrow = 0
        for d, i, p in parts:
            p = np.asarray(p, np.int64)
            datas.append(np.asarray(d, np.float32)); inds.append(np.asarray(i, np.int32))
            ptrs.append(off + p[1:]); off += len(inds[-1]); nrow += len(p) - 1
        ncol = ncol or NFIX + len(self.vocab.idx) + 1
        return sp.csr_matrix((np.concatenate(datas) if datas else np.zeros(0, np.float32),
                              np.concatenate(inds) if inds else np.zeros(0, np.int32),
                              np.concatenate(ptrs)), shape=(nrow, ncol))

    def train(self, givendir, names, negmax=400, rounds=200, leaves=63, seed=1, threads=8,
              weighting='none', negratio=0.0, longexp=0.0, depth=-1, min_data=20, lr=0.1, jobs=1):
        """givendir: a directory, or a dict name -> path. All positives of a log are kept; its negatives are
        subsampled to negmax, or with negratio R > 0 to max(negmax, R x its positives) (negatives scale with the
        proof; the papers' negative/positive ratio as a hyperparameter, Isabelle ENIGMA 4.2).
        weighting 'none': rows weigh 1, positives scaled globally (scale_pos_weight), as before;
        'log' (Suda, CADE 2021, 4.3): every log weighs the same, half on its positives, half on its negatives.
        longexp E: a log's rows weigh (positives / median positives) ** E more (long proofs count more)."""
        import lightgbm as lgb
        rnd = random.Random(seed)
        parts, ys, logs = [], [], []
        if jobs > 1:
            # (19 Nov) forked workers over the logs; the vocab must be frozen first (--vocab-from), so that every
            # worker codes features the same way
            assert self.vocab.frozen, 'jobs > 1 needs a frozen vocab (--vocab-from)'
            global _W
            _W = self
            import multiprocessing as mp_
            todo = [(n, givendir[n] if isinstance(givendir, dict) else os.path.join(givendir, n), negmax, negratio,
                     seed) for n in names]
            with mp_.get_context('fork').Pool(jobs) as P:
                for k, r in enumerate(P.imap(_log_part, todo, chunksize=8)):
                    if r is not None:
                        parts.append(r[0]); ys.extend(r[1].tolist()); logs.append(r[2])
                    if k % 20000 == 0:
                        print(f'  {k} of {len(todo)} logs', flush=True)
            names = []
        for n in names:
            path = givendir[n] if isinstance(givendir, dict) else os.path.join(givendir, n)
            rows = [x for x in load(path, self.parents) if x[0] >= 0]
            pos = [x for x in rows if x[0] == 1]
            neg = [x for x in rows if x[0] == 0]
            if not pos:
                continue
            k = max(negmax, int(round(negratio * len(pos)))) if negratio > 0 else negmax
            if len(neg) > k:
                neg = rnd.sample(neg, k)
            sel = pos + neg
            parts.append(self.rows(n.split('@')[0], [x[1:] for x in sel]))   # (NAME@K: K-th proof of NAME, --list)
            parts[-1] = tuple(np.asarray(z, t) for z, t in zip(parts[-1], (np.float32, np.int32, np.int64)))
            ys.extend(x[0] for x in sel)
            logs.append((len(pos), len(neg)))
        self.vocab.frozen = True
        X = self.matrix(parts)
        del parts
        self.ncol = X.shape[1]
        y = np.array(ys, dtype=np.int8)
        med = float(np.median([p for p, _ in logs])) if logs else 1.0
        w = None
        if weighting == 'log' or longexp:
            w = np.empty(len(y), np.float32); o = 0
            for p_, n_ in logs:
                f = (p_ / med) ** longexp if longexp else 1.0
                if weighting == 'log':
                    w[o:o + p_] = 0.5 * f / p_
                    w[o + p_:o + p_ + n_] = 0.5 * f / max(1, n_)
                else:
                    w[o:o + p_ + n_] = f
                o += p_ + n_
            w *= len(w) / w.sum()
        params = dict(objective='binary', learning_rate=lr, num_leaves=leaves, max_depth=depth,
                      min_data_in_leaf=min_data, feature_fraction=0.5, bagging_fraction=0.8,
                      bagging_freq=1, verbose=-1, num_threads=threads)
        if weighting != 'log':
            params['scale_pos_weight'] = float((y == 0).sum()) / max(1, (y == 1).sum())
        self.model = lgb.train(params, lgb.Dataset(X, y, weight=w), rounds)
        return X.shape, int(y.sum()), len(logs)

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
    ap.add_argument('--list', help='training logs: lines NAME<TAB>PATH, several per goal allowed (Mizar60: '
                    'up to K proofs per problem); with GIVENDIR, which then gives only the test logs')
    ap.add_argument('--negratio', type=float, default=0.0, help='negatives per log: max(negmax, R x positives)')
    ap.add_argument('--weighting', default='none', choices=['none', 'log'],
                    help="'log': every log the same weight, half positives, half negatives (Suda, CADE 2021)")
    ap.add_argument('--long-exp', type=float, default=0.0, help='weigh a log (positives/median) ** E (long proofs)')
    ap.add_argument('--max-depth', type=int, default=-1)
    ap.add_argument('--min-data', type=int, default=20)
    ap.add_argument('--lr', type=float, default=0.1)
    ap.add_argument('--jobs', type=int, default=1, help='feature workers (needs --vocab-from)')
    ap.add_argument('--vocab-from', help="a model's vocab file, frozen: features outside it are dropped")
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--theory', action='store_true', help='add the theory block (axiom features)')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--parents', action='store_true', help='add the parents\' features (p: block)')
    ap.add_argument('--test-origs', help='comma-separated originals to hold out')
    ap.add_argument('--test-names', help='file of problems to hold out (their originals stay in training: the loop setting)')
    ap.add_argument('--save'); ap.add_argument('--vocab')
    ap.add_argument('--load', help='MODEL.txt,VOCAB: evaluate this model on the test problems, no training')
    ap.add_argument('--test-only', action='store_true', help='with --test-names: evaluate on exactly those')
    ap.add_argument('--per', help='write each test problem\'s AUC to this file')
    a = ap.parse_args()
    global THEORY
    THEORY = a.theory
    paths = {}
    for d in a.givendir.split(','):
        if os.path.isdir(d):
            for n in os.listdir(d):
                paths[n] = os.path.join(d, n)
    if a.list:
        tn = set(l.split()[0] for l in open(a.test_names)) if a.test_names else set()
        paths = {n: p for n, p in paths.items() if n in tn}   # (GIVENDIR: the test logs only)
        cnt = collections.Counter()
        for l in open(a.list):
            n, p_ = l.rstrip('\n').split('\t')[:2]
            if n not in tn:
                paths[f'{n}@{cnt[n]}'] = p_; cnt[n] += 1
    names = sorted(paths)
    origs = sorted(set(n.split('__goal_')[0] for n in names))
    random.seed(a.seed); random.shuffle(origs)
    test_o = set() if a.all else set(origs[:max(1, len(origs) // 3)])
    if a.test_origs:
        test_o = set(a.test_origs.split(','))
    test_n = set()
    if a.test_names:
        test_o = set() if not a.test_origs else test_o
        test_n = set(l.split()[0] for l in open(a.test_names))
    train = [n for n in names if n.split('__goal_')[0] not in test_o and n not in test_n]
    test = [n for n in names if n.split('__goal_')[0] in test_o or n in test_n]
    print('test originals', sorted(test_o))
    m = RuleModel(a.parents)
    if a.load:
        import lightgbm as lgb
        mp, vp = a.load.split(',')
        for line in open(vp):
            i, k = line.rstrip('\n').split('\t', 1)
            m.vocab.idx[k] = int(i) - NFIX
        m.vocab.frozen = True
        m.model = lgb.Booster(model_file=mp)
        m.ncol = m.model.num_feature()
    else:
        if a.vocab_from:
            for line in open(a.vocab_from):
                i, k = line.rstrip('\n').split('\t', 1)
                m.vocab.idx[k] = int(i) - NFIX
            m.vocab.frozen = True
        print('train', m.train(paths, train, a.negmax, a.rounds, a.leaves, a.seed, a.threads, a.weighting,
                               a.negratio, a.long_exp, a.max_depth, a.min_data, a.lr, a.jobs), flush=True)
    if a.test_only:
        test = sorted(test_n & set(names))
    if a.save:
        m.save(a.save, a.vocab or a.save + '.vocab')
    random.shuffle(test)
    aucs = []; per = []; stats = collections.defaultdict(list)
    for n in test[:a.ntest]:
        rows = [x for x in load(paths[n], a.parents) if x[0] >= 0]
        if len(rows) < 20 or not any(x[0] == 1 for x in rows):
            continue
        y = np.array([x[0] for x in rows]); s = m.predict(n, [x[1:] for x in rows])
        v = auc(y, s)
        if v is not None:
            aucs.append(v)
            per.append((n, v))
        last = max(i for i, x in enumerate(rows) if x[0] == 1) + 1
        for t in (0.05, 0.1, 0.2, 0.3, 0.5):
            keep = s >= t
            stats[t].append((keep[y == 1].mean(), 1 - keep[y == 0].mean(),
                             keep[:last].sum() / last))
    print(f'AUC {np.mean(aucs):.3f} over {len(aucs)} problems')
    if a.per:
        open(a.per, 'w').write(''.join(f'{n}\t{v:.4f}\n' for n, v in per))
    for t, L in sorted(stats.items()):
        A = np.array(L)
        print(f'threshold {t}: positives kept {A[:,0].mean():.3f}, negatives rejected {A[:,1].mean():.3f}, '
              f'rules until proof kept {A[:,2].mean():.3f}, all-pos-kept {np.mean(A[:,0] == 1):.2f}')


def write_goalfile(name, vocab, path, lits=None):
    """Goal block of the rule model for twee --rule-goal."""
    g = goal_feats(name, lits)
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
