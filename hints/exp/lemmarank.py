"""lemmarank.py: a learned ranker of kNN lemma candidates for plain runs (notes/2026-11-23-lemma-ranker.md).

  lemmarank.py data OUT.pkl DIR... [--trusted T]   (goal, candidate, used) rows with features, from the THM rows of
                                                   exp/condprove.py dirs: candidates are the problem's lemma_knn_<i>_<x>
                                                   axioms (rank i), used those in the proof's Axiom lines
  lemmarank.py eval DATA.pkl [FEATS]               5 folds grouped by the goal's original: recall at 50/100/400 of the
                                                   used kNN lemmas, the model's order against the similarity rank
  lemmarank.py train DATA.pkl MODEL [FEATS] [--exclude SET]  LightGBM on all rows (FEATS: v1 = lr1's, or a comma list;
                                                   SET: its originals' problems left out) (MODEL.txt and MODEL.json: the feature names)

As a module: Ranker(MODEL, trusted).select(goal, k, exclude) re-ranks LemmaIndex.select's top POOL (2,000) by the
model (condprove.py --index learned:MODEL). Features are computed against one context (TRUSTED; production's hints
and kept outputs for the use counts and proof dependencies). LightGBM and numpy on 2 threads."""
import os, sys, re, math, json, pickle, collections
os.environ.setdefault('OMP_NUM_THREADS', '2'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
sys.path.insert(0, '/project/twee/hints')
import lemmas
HW = '/project/hintwork'
HDIR = f'{HW}/loops/UL/hints'
FEATS = ['rank', 'lrank', 'sim', 'simrel', 'same_orig', 'sib_dist', 'same_key', 'len_x', 'len_g', 'len_ratio', 'nvar_x',
         'sym_jac', 'sym_shared', 'sym_xonly', 'uses', 'dep50', 'dep50w', 'pos_x', 'lhint', 'eq_goal']
# (23 Nov 11:40) lr2's features: the goal's proved siblings within 20 goals whose proof steps (deps) or kept output's
# USEDAXIOMS hold the candidate, and the nearest such sibling's distance. A model's .json names its features; rows
# hold all of FEATS2, and a model takes its own columns (lr1: FEATS)
FEATS2 = FEATS + ['sib_dep20', 'sib_used20', 'sib_near']
SYM = re.compile(r'\b([a-z][A-Za-z0-9_]*)\b')
VAR = re.compile(r'\bX\d+\b')

class Ctx:
    """the context the features are computed in: TRUSTED's index with production's use counts and proof steps, or
    (loop.py, 23 Nov) PARTS = (index, uses, deps, hints dir) of a loop"""
    def __init__(self, trusted=None, parts=None):
        if parts:
            self.index, self.uses, self.deps, self.hdir = parts
            solved = set(self.deps)
        else:
            T = sorted({l.split()[0] for l in open(trusted) if l.strip()})
            self.index = lemmas.LemmaIndex(T, subsets=True)
            self.uses = lemmas.lemma_uses([f'{HW}/loops/UL'])
            self.deps, _ = lemmas.proof_deps(HDIR, T)
            self.hdir = HDIR
            solved = set(T)
        self.sibs = collections.defaultdict(list)
        for x in solved:
            o, k = lemmas.split(x); self.sibs[o].append(int(k))
        self._used_by = None; self._sibc = {}
        self.maxk = collections.Counter()
        for l in open(f'{HW}/sets/all'):
            o, k = lemmas.split(l.strip())
            self.maxk[o] = max(self.maxk[o], int(k))
        self._form = {}; self._nb = {}
    def form(self, x):
        f = self._form.get(x)
        if f is None:
            f = self._form[x] = lemmas.lemma_form(x) or ''
        return f
    def used_by(self):
        """target -> the lemma goals its kept output's USEDAXIOMS names (the loop dir above the hints dir)"""
        if self._used_by is None:
            import glob, subprocess
            d = os.path.dirname(self.hdir.rstrip('/'))
            outs = glob.glob(os.path.join(d, 'r*', 'out'))
            ub = collections.defaultdict(set)
            if outs:
                p = subprocess.run(['grep', '-r', '-m1', '^USEDAXIOMS'] + outs, capture_output=True, text=True)
                for line in p.stdout.splitlines():
                    path, _, rest = line.partition(':USEDAXIOMS')
                    t = os.path.basename(path); o = t.rsplit('__goal_', 1)[0]
                    for x in rest.split():
                        m = re.match(r'lemma_knn_\d+_(\S+__goal_\d+)$', x)
                        if m:
                            ub[t].add(m.group(1)); continue
                        m = re.match(r'lemma_goal_(\d+)$', x)
                        if m:
                            ub[t].add(f'{o}__goal_{m.group(1)}')
            self._used_by = ub
        return self._used_by
    def sib_counts(self, g):
        """(deps Counter, used Counter, nearest distance per goal) over G's proved siblings within 20 goals"""
        v = self._sibc.get(g)
        if v is None:
            o, k = lemmas.split(g); k = int(k); ub = self.used_by()
            cd, cu, near = collections.Counter(), collections.Counter(), {}
            for j in self.sibs.get(o, ()):
                if j != k and abs(j - k) <= 20:
                    m = f'{o}__goal_{j}'
                    for x in self.deps.get(m, ()):
                        cd[x] += 1; near[x] = min(near.get(x, 99), abs(j - k))
                    for x in ub.get(m, ()):
                        cu[x] += 1; near[x] = min(near.get(x, 99), abs(j - k))
            v = self._sibc[g] = (cd, cu, near)
        return v
    def neighbours(self, g):
        v = self._nb.get(g)
        if v is None:
            v = self._nb[g] = [(self.index.sim(g, m), m) for m in self.index.select(g, 50)]
        return v
    def features(self, g, cands):
        """rows for G's candidates CANDS, (rank, goal) in similarity order"""
        ix = self.index
        if g not in ix.info:
            ix.select(g, 1)
        og, kg = lemmas.split(g)
        fg = self.form(g); sg = set(SYM.findall(fg)); lg = len(fg)
        nb = self.neighbours(g)
        top = ix.sim(g, cands[0][1]) if cands else 0.0
        keyg = ix.info[g][0]
        cd, cu, near = self.sib_counts(g)
        # (23 Nov 11:50) a solved goal's own kept output is not counted in the use counts (it leaked the label into
        # lr1's training rows of solved goals, RKD1); an unsolved goal has none
        own = self.used_by().get(g, ())
        rows = []
        for r, x in cands:
            ox, kx = lemmas.split(x)
            fx = self.form(x); sx = set(SYM.findall(fx))
            s = ix.sim(g, x)
            d50 = [sm for sm, m in nb if x in self.deps.get(m, ())]
            try:
                hb = os.path.getsize(f'{self.hdir}/{x}')
            except OSError:
                hb = 0
            rows.append([r, math.log1p(r), s, s / top if top > 0 else 0.0, float(ox == og),
                         abs(int(kx) - int(kg)) if ox == og else -1, float(ix.info.get(x, (None,))[0] == keyg),
                         len(fx), lg, len(fx) / max(1, lg), len(set(VAR.findall(fx))),
                         len(sx & sg) / max(1, len(sx | sg)), len(sx & sg), len(sx - sg),
                         math.log1p(max(0, self.uses.get(x, 0) - (x in own))), len(d50), sum(d50), int(kx) / max(1, self.maxk[ox]),
                         math.log1p(hb), float(fx == fg), cd.get(x, 0), cu.get(x, 0), near.get(x, 99)])
        return rows

AX = re.compile(r'^Axiom \d+ \(([^)]*)\)')
KNN = re.compile(r'fof\(lemma_knn_(\d+)_(\S+?__goal_\d+),axiom,')

def cmd_data(out, dirs, trusted):
    ctx = Ctx(trusted)
    X, y, grp, meta = [], [], [], []
    for d in dirs:
        n = 0
        for l in open(f'{d}/results.tsv'):
            f = l.rstrip('\n').split('\t')
            if len(f) < 2 or f[1] != 'THM' or not os.path.exists(f'{d}/proofs/{f[0]}'):
                continue
            g = f[0]
            cands = [(int(i), x) for i, x in KNN.findall(open(f'{d}/p/{g}.p').read())]
            used = {m[1] for t in open(f'{d}/proofs/{g}') for m in [AX.match(t)] if m}
            pos = {x for i, x in cands if f'lemma_knn_{i}_{x}' in used}
            if not pos or any(ctx.form(x) == ctx.form(g) for x in pos):
                continue   # no kNN lemma used, or one that states the goal itself
            cands.sort()
            for row, (i, x) in zip(ctx.features(g, cands), cands):
                X.append(row); y.append(int(x in pos)); grp.append(len(meta));
            meta.append((d, g, len(cands), len(pos)))
            n += 1
        print(f'lemmarank: {d}: {n} problems', flush=True)
    pickle.dump({'X': X, 'y': y, 'grp': grp, 'meta': meta, 'feats': FEATS2}, open(out, 'wb'))
    print(f'lemmarank: {len(meta)} problems, {len(y):,} rows, {sum(y):,} positives -> {out}')

def model(n=None):
    import lightgbm as lgb
    return lgb.LGBMClassifier(n_estimators=n or 300, learning_rate=0.05, num_leaves=31, min_child_samples=20,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=2, verbose=-1)

def cols_of(D, feats):
    """(23 Nov) the columns of D's rows for FEATS ('v1': lr1's features; '' : all)"""
    fs = FEATS if feats == 'v1' else (feats.split(',') if feats else D['feats'])
    return [D['feats'].index(f) for f in fs], fs

def cmd_eval(data, feats=''):
    import numpy as np
    D = pickle.load(open(data, 'rb'))
    cols, fs = cols_of(D, feats)
    X = np.array(D['X'])[:, cols]; y = np.array(D['y']); grp = np.array(D['grp']); meta = D['meta']
    orig = np.array([lemmas.split(meta[i][1])[0] for i in grp])
    uo = sorted(set(orig)); fold = {o: i % 5 for i, o in enumerate(uo)}
    fo = np.array([fold[o] for o in orig])
    score = np.zeros(len(y))
    for k in range(5):
        tr, te = fo != k, fo == k
        m = model().fit(X[tr], y[tr]); score[te] = m.predict_proba(X[te])[:, 1]
    res = collections.defaultdict(lambda: collections.defaultdict(list))
    for p in range(len(meta)):
        sel = grp == p; ys = y[sel]; r = X[sel, 0]; s = score[sel]; n = len(ys)
        for K in (50, 100, 400):
            if n <= K:
                continue
            a = ys[np.argsort(r, kind='stable')][:K].sum() / ys.sum()
            b = ys[np.argsort(-s, kind='stable')][:K].sum() / ys.sum()
            full_a = float(ys[np.argsort(r, kind='stable')][:K].sum() == ys.sum())
            full_b = float(ys[np.argsort(-s, kind='stable')][:K].sum() == ys.sum())
            res[meta[p][0]][K].append((a, b, full_a, full_b))
    print('| dir | K | problems | recall, similarity | recall, model | all used in top K, similarity | all used, model |')
    print('|---|---:|---:|---:|---:|---:|---:|')
    for d in res:
        for K in sorted(res[d]):
            v = np.array(res[d][K])
            print(f'| {d} | {K} | {len(v)} | {v[:,0].mean():.3f} | {v[:,1].mean():.3f} | {v[:,2].mean():.3f} | {v[:,3].mean():.3f} |')
    m = model().fit(X, y)
    imp = sorted(zip(m.booster_.feature_importance('gain'), fs), reverse=True)
    print('gain:', ', '.join(f'{f} {g:.0f}' for g, f in imp))

def cmd_train(data, out, feats='', exclude=''):
    """(23 Nov) EXCLUDE: a goal set whose originals' problems are left out (a model for a test on that set)"""
    import numpy as np
    D = pickle.load(open(data, 'rb'))
    cols, fs = cols_of(D, feats)
    X = np.array(D['X'])[:, cols]; y = np.array(D['y'])
    if exclude:
        eo = {lemmas.split(l.strip())[0] for l in open(exclude) if l.strip()}
        keep = np.array([lemmas.split(D['meta'][i][1])[0] not in eo for i in D['grp']])
        print(f'lemmarank: {exclude}: {len(set(np.array(D["grp"])[keep].tolist()))} of {len(D["meta"])} problems kept', flush=True)
        X, y = X[keep], y[keep]
    m = model().fit(X, y)
    m.booster_.save_model(out + '.txt')
    json.dump({'feats': fs, 'exclude': exclude}, open(out + '.json', 'w'))
    print(f'lemmarank: model {out}.txt from {len(y):,} rows ({int(y.sum()):,} used)')

class Trees:
    """(23 Nov) LightGBM's text model evaluated with numpy (raw scores), for pythons without lightgbm (loop.py,
    production); numeric splits only (x <= threshold goes left; no missing values in these features)"""
    def __init__(self, path):
        import numpy as np
        self.trees = []
        cur = None
        for l in open(path):
            l = l.strip()
            if l.startswith('Tree='):
                cur = {}; self.trees.append(cur)
            elif cur is not None and '=' in l and not l.startswith('end of trees'):
                k, v = l.split('=', 1)
                if k in ('split_feature', 'left_child', 'right_child'):
                    cur[k] = np.array([int(x) for x in v.split()], dtype=np.int64)
                elif k in ('threshold', 'leaf_value'):
                    cur[k] = np.array([float(x) for x in v.split()])
                elif k == 'decision_type':
                    assert all(int(x) & 1 == 0 for x in v.split()), 'categorical split'
                elif k == 'num_leaves':
                    cur[k] = int(v)
            elif l.startswith('end of trees'):
                break
    def predict(self, X):
        import numpy as np
        X = np.asarray(X, dtype=float); out = np.zeros(len(X)); rows = np.arange(len(X))
        for t in self.trees:
            if t['num_leaves'] == 1:
                out += t['leaf_value'][0]; continue
            node = np.zeros(len(X), dtype=np.int64)
            while True:
                m = node >= 0
                if not m.any():
                    break
                n = node[m]
                left = X[rows[m], t['split_feature'][n]] <= t['threshold'][n]
                node[m] = np.where(left, t['left_child'][n], t['right_child'][n])
            out += t['leaf_value'][-node - 1]
        return out

class Ranker:
    """condprove.py --index learned:MODEL; lightgbm if it is there, else Trees"""
    POOL = 2000
    MIX = 0
    def __init__(self, path, trusted=None, ctx=None):
        fs = json.load(open(path + '.json'))['feats']
        self.cols = [FEATS2.index(f) for f in fs]
        try:
            import lightgbm as lgb
            b = lgb.Booster(model_file=path + '.txt'); self.score = lambda X: b.predict(X, num_threads=2)
        except ImportError:
            t = Trees(path + '.txt'); self.score = t.predict
        self.ctx = ctx or Ctx(trusted)
    def select(self, g, k, exclude=()):
        import numpy as np
        C = self.ctx.index.select(g, self.POOL, exclude=exclude)
        if len(C) <= k:
            return C
        s = self.score(np.array(self.ctx.features(g, list(enumerate(C))))[:, self.cols])
        # (23 Nov, MIX) the similarity list's top MIX first, then the model's best of the rest: in the Z9-gap pre-check
        # similarity's 30-lemma proofs used clusters of their lemmas, which the model's 30 mostly lacked (notes, "clusters")
        h = min(self.MIX, k)
        order = [i for i in np.argsort(-s, kind='stable') if i >= h][:k - h]
        return C[:h] + [C[i] for i in order]

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'data':
        tr = f'{HW}/loops/TRUSTNOW/t0641.trusted'
        if '--trusted' in a:
            i = a.index('--trusted'); tr = a[i + 1]; a = a[:i] + a[i + 2:]
        cmd_data(a[1], a[2:], tr)
    elif a[0] == 'eval':
        cmd_eval(a[1], a[2] if len(a) > 2 else '')
    elif a[0] == 'train':
        ex_ = a[a.index('--exclude') + 1] if '--exclude' in a else ''
        a = [x for x in a if x not in ('--exclude', ex_)] if ex_ else a
        cmd_train(a[1], a[2], a[3] if len(a) > 3 else '', ex_)
