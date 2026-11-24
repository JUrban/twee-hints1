#!/usr/bin/env python3
"""Lemma import: add the statements of proven sibling goals as axioms.

All goals X__goal_N of one original X have the same axioms, so a sibling
goal proven from them is a theorem of the theory and a sound extra axiom.
(As in CASC LTB, where conjectures proven earlier in a batch may be used.)

lemmas.py NAMES SOLVED OUTDIR [-m M] [--after]
  NAMES   problems to write
  SOLVED  file whose first column lists proven problems
  OUTDIR  gets OUTDIR/<name>.p: the problem plus up to M lemmas, the
          proven siblings with the nearest goal numbers below N (with
          --after also above N). Only unit equations are used.
  --knn K adds up to K more lemmas: the proven goals most similar to the
          target goal (idf-weighted Jaccard on term-shape features) among
          all problems with the same axioms, from any original.
  --pool F[,F...] extra files of proven problems for --knn.
  --subsets: --knn may also use problems whose axioms are a subset of the
          target's (theorems of a weaker theory), not only equal ones.
"""
import argparse, collections, hashlib, math, os, pickle, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROB = os.environ.get('AIM_PROB', '/project/AIM60k/problems/tptp')   # (16 Nov) AIM_PROB: another problem dir
CACHE = '/project/hintwork/abs/goalinfo.pkl'

def split(name):
    o, n = name.rsplit('__goal_', 1)
    return o, int(n)

_conj = {}

def conjecture(name):
    # (21 Nov) cached: loop.py's kNN picks asked for it at every dispatch of a goal lemma_form cannot unitize, a read
    # and a regex over the problem file each time, 15% of the main thread at 12 workers (notes/2026-11-21-dispatch-profile.md)
    v = _conj.get(name, False)
    if v is not False:
        return v
    txt = open(os.path.join(PROB, name + '.p')).read()
    m = re.search(r'fof\(\w+,\s*conjecture,\s*(.*)\)\.\s*$', txt, re.S)
    v = _conj[name] = m.group(1).strip() if m else None
    return v

# A conditional conjecture ~ s = X | C = D (or ~ X = s | C = D) whose hypothesis binds a variable X
# that does not occur in s is equivalent to the unit equation C = D with X replaced by s: 6,235 of
# AIM60k's 9,052 conditional goals (15 Nov; Prover9 proved stalled goals with such siblings, which
# lemma import had skipped). TWEE_LEMMA_UNITIZE=0 turns the conversion off (controls).
UNITIZE = os.environ.get('TWEE_LEMMA_UNITIZE', '1') != '0'
_VAR = re.compile(r'X\d+')

def unitize(f):
    """The unit-equation fof formula equivalent to conjecture F, or None."""
    body = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', f).strip()
    while body.startswith('(') and body.endswith(')'):
        body = body[1:-1].strip()
    if any(c in body for c in ('=>', '&', '<')):
        return None
    lits = [x.strip() for x in body.split('|')]
    if len(lits) != 2:
        return None
    neg = [x for x in lits if x.startswith('~')]; pos = [x for x in lits if not x.startswith('~')]
    if len(neg) != 1 or len(pos) != 1 or '!=' in pos[0] or pos[0].count('=') != 1:
        return None
    h = neg[0][1:].strip()
    while h.startswith('(') and h.endswith(')'):
        h = h[1:-1].strip()
    if h.count('=') != 1 or '!=' in h:
        return None
    a, b = (x.strip() for x in h.split('='))
    for v, t in ((b, a), (a, b)):
        if _VAR.fullmatch(v) and not re.search(r'\b%s\b' % v, t):
            c, d = (re.sub(r'\b%s\b' % v, t, x.strip()) for x in pos[0].split('='))
            if c == d:
                return None
            vs = sorted(set(_VAR.findall(c + ' ' + d)), key=lambda x: int(x[1:]))
            eq = f'{c} = {d}'
            return f'! [{",".join(vs)}] : ({eq})' if vs else eq
    return None

_lform = {}
def lemma_form(name):
    """NAME's conjecture as a unit-equation axiom formula (unitize for conditional ones), or None."""
    if name not in _lform:
        f = conjecture(name)
        _lform[name] = None if not f else f if unit_eq(f) else (unitize(f) if UNITIZE else None)
    return _lform[name]

def negated_goal(name, tag):
    """The conjecture of NAME as a skolemised negated_conjecture body (constants
    sk<TAG>x<i>), or None unless it is a universally quantified unit equation."""
    f = conjecture(name)
    if not f or not unit_eq(f):
        return None
    vs = []
    while True:
        q = re.match(r'!\s*\[([^\]]*)\]\s*:\s*(.*)$', f, re.S)
        if not q:
            break
        vs += [v.strip() for v in q.group(1).split(',')]
        f = q.group(2).strip()
    while f.startswith('(') and f.endswith(')'):
        f = f[1:-1].strip()
    for i, v in enumerate(vs):
        f = re.sub(r'\b%s\b' % re.escape(v), f'sk{tag}x{i}', f)
    l, r = f.split('=')
    return f'{l.strip()} != {r.strip()}'

def unit_eq(f):
    body = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', f)
    return not any(c in body for c in ('|', '~', '=>', '&', '!=')) and body.count('=') == 1

def by_original(names):
    solved = collections.defaultdict(set)
    for n in names:
        o, k = split(n)
        solved[o].add(k)
    return solved

def lemma_problem(name, solved, m, after=False):
    """Text of problem NAME with up to M proven siblings (solved: original ->
    set of goal numbers) as extra axioms, and the number of lemmas added."""
    o, k = split(name)
    cands = sorted((j for j in solved.get(o, ()) if j != k and (after or j < k)), key=lambda j: (abs(k - j), j))
    lem = []
    for j in cands:
        if len(lem) >= m:
            break
        f = lemma_form(f'{o}__goal_{j}')
        if f:
            lem.append((j, f))
    txt = open(os.path.join(PROB, name + '.p')).read().rstrip('\n') + '\n'
    for j, f in lem:
        txt += f'fof(lemma_goal_{j},axiom,{f}).\n'
    return txt, len(lem)

_axkey = {}
def axiom_key(name):
    """Hash of the sorted axiom lines: problems with equal keys have the same axioms."""
    if name not in _axkey:
        ax = sorted(l.strip() for l in open(os.path.join(PROB, name + '.p'))
                    if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l)
        _axkey[name] = hashlib.md5('\n'.join(ax).encode()).hexdigest()
    return _axkey[name]

def goal_info(names):
    """name -> (axiom key, goal features), cached on disk."""
    import hintsel
    info = pickle.load(open(CACHE, 'rb')) if os.path.exists(CACHE) else {}
    new = [n for n in names if n not in info]
    for n in new:
        try:
            F = frozenset(hintsel.goal_features(n, 3))
        except Exception:
            F = frozenset()
        info[n] = (axiom_key(n), F)
    if new:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        tmp = CACHE + '.tmp%d' % os.getpid(); pickle.dump(info, open(tmp, 'wb')); os.replace(tmp, CACHE)
    return info

_axset = {}
def axiom_set(name):
    """The axioms of NAME's original as a set of clause bodies (names dropped)."""
    o, _ = split(name)
    if o not in _axset:
        out = set()
        for l in open(os.path.join(PROB, name + '.p')):
            if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l:
                out.add(re.sub(r'\s+', '', l.split(',', 2)[2].rsplit(')', 1)[0]))
        _axset[o] = frozenset(out)
    return _axset[o]

def lemma_uses(dirs, exclude=()):
    """source goal -> number of proofs whose USEDAXIOMS name it as a lemma (kNN lemma_knn_<i>_<goal> or sibling
    lemma_goal_<j>), over the kept outputs DIR/r*/out/<target> of each loop DIR; targets in EXCLUDE are skipped."""
    import glob, subprocess
    cnt = collections.Counter()
    outs = [g for d in dirs for g in glob.glob(os.path.join(d, 'r*', 'out'))]
    if not outs:
        return cnt
    p = subprocess.run(['grep', '-r', '-m1', '^USEDAXIOMS'] + outs, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        path, _, rest = line.partition(':USEDAXIOMS')
        tgt = os.path.basename(path)
        if tgt in exclude:
            continue
        o = tgt.rsplit('__goal_', 1)[0]
        srcs = set()
        for x in rest.split():
            m = re.match(r'lemma_knn_\d+_(\S+__goal_\d+)$', x)
            if m:
                srcs.add(m.group(1)); continue
            m = re.match(r'lemma_goal_(\d+)$', x)
            if m:
                srcs.add(f'{o}__goal_{m.group(1)}')
        cnt.update(srcs)
    return cnt

def proof_deps(hints_dir, solved):
    """(MaSh-style kNN lemmas, 16 Nov) proof -> the proven unit goals of the same or weaker axioms whose equation
    (canonical, as transfer.key) is a step of its proof (HINTS_DIR/<goal>), besides its own goal; and their idf
    (log(proofs / proofs that have the goal as a step)). About 20 s for 44k proofs."""
    import transfer, hintsel
    keyof = {}
    for n in solved:
        if not lemma_form(n):
            continue
        try:
            lits = hintsel.goal_lits(n)
        except Exception:
            continue
        if len(lits) == 1 and lits[0][0]:
            keyof[n] = transfer.key(lits[0][1], lits[0][2])
    want = collections.defaultdict(list)
    for n, k in keyof.items():
        want[k].append(n)
    deps = {}
    for f in solved:
        try:
            lines = open(os.path.join(hints_dir, f)).read().splitlines()
        except OSError:
            continue
        A = axiom_set(f); kf = keyof.get(f); out = set()
        for x in lines:
            w = x.split('\t')
            if len(w) >= 2 and (w[0], w[1]) != kf:
                for g in want.get((w[0], w[1]), ()):
                    if g != f and axiom_set(g) <= A:
                        out.add(g)
        if out:
            deps[f] = frozenset(out)
    df = collections.Counter(g for v in deps.values() for g in v)
    N = max(1, len(deps))
    return deps, {g: math.log(N / c) / math.log(N + 1) for g, c in df.items()}

class LemmaIndex:
    """Proven unit-equation goals grouped by axiom set, for similarity search.
    With subsets=True, a target may use the goals of every problem whose axioms
    are a subset of its own (theorems of a weaker theory hold in the stronger)."""
    def __init__(self, solved_names, subsets=False, uses=None, pop=0.0, deps=None, dep_w=0.0, dep_n=50):
        names = [n for n in solved_names if lemma_form(n)]
        self.info = goal_info(names)
        self.subsets = subsets
        # (16 Nov) POP > 0: a candidate's similarity is multiplied by 1 + POP * log(1 + USES[m]), USES[m] = the
        # number of proofs that used m as a lemma (lemma_uses)
        self.uses = uses or {}
        self.pop = pop
        # (16 Nov) DEP_W > 0 (deps = proof_deps(..)): MaSh-style kNN; a lemma scores the similarity of each of the
        # DEP_N nearest proven goals it is, plus DEP_W x similarity x idf / sqrt(#deps) for each whose proof has it
        # as a step
        self.deps, self.dep_idf = deps if deps else ({}, {})
        self.dep_w = dep_w
        self.dep_n = dep_n
        self.groups = collections.defaultdict(list)
        self.sets = {}
        for n in names:
            k = self.info[n][0]
            self.groups[k].append(n)
            if k not in self.sets:
                self.sets[k] = axiom_set(n)
        self._idf = {}
        self._cands = {}
        # (17 Nov) select() memo: the loop picks a goal's kNN lemmas at dispatch (--retry-knn) and again when it
        # writes the problem, ~20-40 ms each over 20k+ candidates (Z0); the index is rebuilt, not changed
        self._memo = {}
        self._cset = {}

    def candidates(self, key, name):
        if key not in self._cands:
            if self.subsets:
                S = axiom_set(name)
                ks = [k for k, A in self.sets.items() if A <= S]
            else:
                ks = [key] if key in self.groups else []
            self._cands[key] = [m for k in ks for m in self.groups[k]]
        return self._cands[key]

    def idf(self, key, name=None):
        if key not in self._idf:
            g = self.candidates(key, name)
            df = collections.Counter(x for n in g for x in self.info[n][1])
            self._idf[key] = {x: math.log((len(g) + 1) / c) for x, c in df.items()}
        return self._idf[key]

    def select_in(self, name, k, B, A, exclude=()):
        """The K proven goals most similar to NAME's goal among those of theories within axiom set B
        but not within A (climb.py --theories: theorems of a stronger theory B for a sketch of NAME)."""
        if name not in self.info:
            import hintsel
            try:
                F = frozenset(hintsel.goal_features(name, 3))
            except Exception:
                F = frozenset()
            self.info[name] = (axiom_key(name), F)
        F = self.info[name][1]
        scored = []
        for kk, S in self.sets.items():
            if S <= B and not S <= A:
                for m in self.groups[kk]:
                    if m in exclude:
                        continue
                    G = self.info[m][1]
                    if F and G:
                        scored.append((len(F & G) / len(F | G), m))
        scored.sort(key=lambda x: (-x[0], x[1]))
        out, seen = [], set()
        for _, m in scored:
            f = lemma_form(m)
            if f and f not in seen:
                seen.add(f); out.append(m)
                if len(out) >= k:
                    break
        return out

    def select(self, name, k, exclude=(), eq=None):
        """The K proven goals with the same axioms most similar to NAME's goal
        (EQ: (lhs, rhs) of another goal over NAME's axioms, a cut, instead)."""
        if eq is not None:
            import feats
            key = self.info[name][0] if name in self.info else axiom_key(name)
            return self._select(name, key, frozenset(feats.features(eq[0], eq[1], 3)), k, exclude, None)
        mk = (name, k, frozenset(exclude))
        v = self._memo.get(mk)
        if v is not None:
            return list(v)
        if name not in self.info:  # targets: in memory only, no cache write
            import hintsel
            try:
                F = frozenset(hintsel.goal_features(name, 3))
            except Exception:
                F = frozenset()
            self.info[name] = (axiom_key(name), F)
        key, F = self.info[name]
        out = self._select(name, key, F, k, exclude, lemma_form(name) or conjecture(name))
        self._memo[mk] = tuple(out)
        return out

    def sim(self, name, m):
        """(21 Nov 00:52) _select's score of proven goal M for NAME's goal (0 if M is not in NAME's pool); NAME must
        have been selected for (its features are in self.info). loop.py --knn-ctx: does a new proof enter a goal's
        kNN lemmas?"""
        key, F = self.info[name]
        cs = self._cset.get(key)
        if cs is None:
            cs = self._cset[key] = frozenset(self.candidates(key, name))
        if m not in cs or m == name or not F:
            return 0.0
        idf = self.idf(key, name)
        G = self.info[m][1]
        inter = sum(idf[x] for x in F & G)
        if inter <= 0:
            return 0.0
        union = sum(idf.get(x, 0) for x in F) + sum(idf[x] for x in G) - inter
        sc = inter / union
        if self.pop:
            sc *= 1 + self.pop * math.log1p(self.uses.get(m, 0))
        return sc

    def _select(self, name, key, F, k, exclude, form):
        idf = self.idf(key, name)
        wF = sum(idf.get(x, 0) for x in F)
        scored = []
        for m in self.candidates(key, name):
            if m == name or m in exclude:
                continue
            G = self.info[m][1]
            inter = sum(idf[x] for x in F & G)
            if inter <= 0:
                continue
            union = wF + sum(idf[x] for x in G) - inter
            sc = inter / union
            if self.pop:
                sc *= 1 + self.pop * math.log1p(self.uses.get(m, 0))
            scored.append((sc, m))
        scored.sort(key=lambda x: (-x[0], x[1]))
        if self.dep_w and self.deps:
            cand = set(self.candidates(key, name))
            acc = collections.defaultdict(float)
            for sc, m in scored[:self.dep_n]:
                acc[m] += sc
                D = self.deps.get(m)
                if D:
                    w = self.dep_w * sc / math.sqrt(len(D))
                    for g in D:
                        if g in cand and g != name and g not in exclude:
                            acc[g] += w * self.dep_idf.get(g, 0.0)
            scored = sorted(((v, m) for m, v in acc.items()), key=lambda x: (-x[0], x[1]))
        # (16 Nov) seen was {form}, which dropped every proven goal stating exactly the target: but such a goal of
        # the same or a weaker theory proves it (46 of transfer.py's 63 source-lemma proofs were of this kind)
        out, seen = [], set()
        for _, m in scored:
            f = lemma_form(m)
            if f in seen:
                continue
            seen.add(f); out.append(m)
            if len(out) >= k:
                break
        return out

def sibling_lemmas(name, solved, m, after=False):
    """The goal numbers lemma_problem picks: up to M nearest proven siblings with a lemma form."""
    o, k = split(name)
    cands = sorted((j for j in solved.get(o, ()) if j != k and (after or j < k)), key=lambda j: (abs(k - j), j))
    out = []
    for j in cands:
        if len(out) >= m:
            break
        if lemma_form(f'{o}__goal_{j}'):
            out.append(j)
    return out

def knn_picks(name, solved, m, index, k, after=False):
    """The goals lemma_problem_knn takes from INDEX (beside NAME's M sibling lemmas)."""
    o, _ = split(name)
    return index.select(name, k, exclude={f'{o}__goal_{j}' for j in sibling_lemmas(name, solved, m, after)})

def lemma_problem_knn(name, solved, m, index, k, after=False, skip=0):
    """lemma_problem plus up to K lemmas from INDEX (same axioms, any original). (24 Nov, exp82) SKIP: the K lemmas
    after the first SKIP of the ranking (ranks SKIP..SKIP+K-1, named by their rank), a disjoint slice of the list."""
    txt, n = lemma_problem(name, solved, m, after)
    have = set(re.findall(r'fof\(lemma_goal_(\d+),', txt))
    o, _ = split(name)
    extra = index.select(name, k + skip, exclude={f'{o}__goal_{j}' for j in have})[skip:]
    for i, x in enumerate(extra, skip):
        txt += f'fof(lemma_knn_{i}_{x},axiom,{lemma_form(x)}).\n'   # (source goal in the name: USEDAXIOMS)
    return txt, n + len(extra)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('solved'); ap.add_argument('outdir')
    ap.add_argument('-m', type=int, default=10)
    ap.add_argument('--after', action='store_true')
    ap.add_argument('--knn', type=int, default=0)
    ap.add_argument('--pool', default='')
    ap.add_argument('--subsets', action='store_true', help='--knn also from problems whose axioms are a subset')
    a = ap.parse_args()
    solved_names = [line.split()[0] for line in open(a.solved) if line.strip()]
    solved = by_original(solved_names)
    index = None
    if a.knn:
        pool = set(solved_names)
        for f in filter(None, a.pool.split(',')):
            pool |= {line.split()[0] for line in open(f) if line.strip()}
        index = LemmaIndex(sorted(pool), subsets=a.subsets)
    os.makedirs(a.outdir, exist_ok=True)
    tot = 0
    for line in open(a.names):
        name = line.split()[0]
        if index:
            txt, n = lemma_problem_knn(name, solved, a.m, index, a.knn, a.after)
        else:
            txt, n = lemma_problem(name, solved, a.m, a.after)
        with open(os.path.join(a.outdir, name + '.p'), 'w') as out:
            out.write(txt)
        tot += n
    print('lemmas', tot)

if __name__ == '__main__':
    main()
