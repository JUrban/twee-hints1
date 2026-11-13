"""Hint selection: rank hints from proofs of solved problems for a target goal.

KNN: find the K solved problems whose goal statements are most similar
(idf-weighted Jaccard on term-shape features), score each hint by the sum
of similarities of the neighbours whose proofs contain it, take the top N.
"""
import collections, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feats

PROB = '/project/AIM60k/problems/tptp'

def goal_of_problem(name):
    """(lhs, rhs) of the conjecture of a TPTP problem, variables uppercase."""
    txt = open(os.path.join(PROB, name + '.p')).read()
    i = txt.index(',conjecture,')
    body = txt[i + len(',conjecture,'):txt.rindex(').')]
    body = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', body).strip()
    while body.startswith('(') and body.endswith(')'):
        body = body[1:-1].strip()
    l, r = body.split(' = ') if ' = ' in body else body.split('=')
    return l.strip(), r.strip()

def goal_lits(name):
    """Literals of the conjecture as (positive, lhs, rhs) triples."""
    txt = open(os.path.join(PROB, name + '.p')).read()
    i = txt.index(',conjecture,')
    body = txt[i + len(',conjecture,'):txt.rindex(').')]
    body = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', body).strip()
    while body.startswith('(') and body.endswith(')'):
        body = body[1:-1].strip()
    out = []
    for lit in body.split('|'):
        lit = lit.strip()
        pos = not lit.startswith('~')
        lit = lit.lstrip('~').strip()
        while lit.startswith('(') and lit.endswith(')'):
            lit = lit[1:-1].strip()
        if '!=' in lit:
            pos = not pos; l, r = lit.split('!=')
        else:
            l, r = lit.split('=')
        out.append((pos, l.strip(), r.strip()))
    return out

def goal_features(name, depth, fallback=None):
    """Term-shape features of all literals of the conjecture."""
    try:
        lits = goal_lits(name)
    except Exception:
        if fallback is None:
            raise
        l, r = fallback.split('\t')
        lits = [(True, l, r)]
    F = set()
    for _, l, r in lits:
        F |= feats.features(l, r, depth)
    return F

class KNN:
    def __init__(self, hintdir, names=None, depth=3):
        self.hints = {}
        self.feats = {}
        self.depth = depth
        for n in (names if names is not None else os.listdir(hintdir)):
            p = os.path.join(hintdir, n)
            if not os.path.exists(p):
                continue
            L = [l.rstrip('\n') for l in open(p) if '\t' in l]
            if not L:
                continue
            self.add(n, L)
        self._idf = None

    def add(self, name, hint_lines):
        self.hints[name] = hint_lines
        self.feats[name] = goal_features(name, self.depth, hint_lines[-1])
        self._idf = None
        self._index = None

    def idf(self):
        if self._idf is None:
            df = collections.Counter(x for f in self.feats.values() for x in f)
            n = len(self.feats)
            self._idf = {x: math.log((n + 1) / c) for x, c in df.items()}
        return self._idf

    def index(self):
        """Sparse matrix of the pool's features (rows = solved problems)."""
        if getattr(self, '_index', None) is None:
            import numpy as np, scipy.sparse as sp
            idf = self.idf()
            names = list(self.feats)
            col = {x: i for i, x in enumerate(idf)}
            ind, ptr = [], [0]
            for m in names:
                ind.extend(col[x] for x in self.feats[m]); ptr.append(len(ind))
            X = sp.csr_matrix((np.ones(len(ind)), np.array(ind, dtype=np.int64), np.array(ptr, dtype=np.int64)),
                              shape=(len(names), len(col)))
            w = np.array([idf[x] for x in col])
            self._index = (names, col, X, w, X @ w, {m: i for i, m in enumerate(names)})
        return self._index

    def axiom_mask(self, name):
        """Boolean mask of pool problems whose axioms are a subset of NAME's."""
        import numpy as np, lemmas
        names = self.index()[0]
        if not hasattr(self, '_axs'):
            self._axs = [lemmas.axiom_set(m) for m in names]
        S = lemmas.axiom_set(name)
        return np.array([A <= S for A in self._axs])

    def neighbours(self, name, F, exclude_self=True, same_orig=False):
        """(similarity, name) of the pool problems sharing a feature with F,
        best first; the same as the plain loop over self.feats, vectorised."""
        import numpy as np
        names, col, X, w, wG, pos = self.index()
        cs = [col[x] for x in F if x in col]
        if not cs:
            return []
        q = np.zeros(X.shape[1]); q[cs] = w[cs]
        I = X @ q
        S = I / (q.sum() + wG - I)
        S[I == 0] = -1
        if exclude_self and name in pos:
            S[pos[name]] = -1
        if same_orig:
            o = name.split('__goal_')[0]
            S[[i for i, m in enumerate(names) if m.split('__goal_')[0] != o]] = -1
        return S, names

    def select(self, name, k=30, topn=100, exclude_self=True, same_orig=False, scores=False, groups=False,
               subsets=False):
        """subsets: only neighbours whose axioms are a subset of NAME's, so
        that their proof lemmas are theorems of NAME's theory."""
        import numpy as np
        try:
            F = goal_features(name, self.depth)
        except Exception:
            F = self.feats.get(name, set())
        r = self.neighbours(name, F, exclude_self, same_orig)
        sims = []
        if r:
            S, names = r
            if subsets:
                S = np.where(self.axiom_mask(name), S, -1)
            good = np.flatnonzero(S > -1)
            if len(good) > k:
                thr = np.partition(S[good], len(good) - k)[len(good) - k]
                good = good[S[good] >= thr]
            sims = sorted(((S[i], names[i]) for i in good), reverse=True)
        sc = collections.Counter()
        grp = collections.defaultdict(list)
        for j, (s, m) in enumerate(sims[:k]):
            for h in self.hints[m]:
                sc[h] += s
                if not grp[h] or grp[h][-1] != j:
                    grp[h].append(j)
        if groups:
            return [(h, grp[h]) for h, _ in sc.most_common(topn)]
        if scores:
            return sc.most_common(topn)
        return [h for h, _ in sc.most_common(topn)]

def knnfiles_main(argv):
    """hintsel.py knnfiles POOLDIR[,POOLDIR...] NAMES OUTDIR [K TOPN] [--subsets]:
    write the kNN hints of each problem in NAMES to OUTDIR/<name>."""
    subsets = '--subsets' in argv
    argv = [x for x in argv if x != '--subsets']
    pools, names_path, outdir = argv[:3]
    k, topn = (int(argv[3]), int(argv[4])) if len(argv) > 4 else (30, 100)
    knn = None
    for d in pools.split(','):
        if knn is None:
            knn = KNN(d)
        else:
            for f in os.listdir(d):
                if f not in knn.hints:
                    L = [l.rstrip('\n') for l in open(os.path.join(d, f)) if '\t' in l]
                    if L:
                        knn.add(f, L)
    os.makedirs(outdir, exist_ok=True)
    for line in open(names_path):
        n = line.split()[0]
        hs = knn.select(n, k, topn, subsets=subsets)
        if hs:
            with open(os.path.join(outdir, n), 'w') as f:
                f.write('\n'.join(hs) + '\n')

if __name__ == '__main__' and sys.argv[1:2] == ['knnfiles']:
    knnfiles_main(sys.argv[2:])
