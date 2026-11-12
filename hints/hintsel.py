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

    def idf(self):
        if self._idf is None:
            df = collections.Counter(x for f in self.feats.values() for x in f)
            n = len(self.feats)
            self._idf = {x: math.log((n + 1) / c) for x, c in df.items()}
        return self._idf

    def select(self, name, k=30, topn=100, exclude_self=True, same_orig=False, scores=False):
        idf = self.idf()
        try:
            F = goal_features(name, self.depth)
        except Exception:
            F = self.feats.get(name, set())
        o = name.split('__goal_')[0]
        sims = []
        for m, G in self.feats.items():
            if exclude_self and m == name:
                continue
            if same_orig and m.split('__goal_')[0] != o:
                continue
            i = sum(idf.get(x, 0) for x in F & G)
            if i == 0:
                continue
            u = sum(idf.get(x, 0) for x in F | G)
            sims.append((i / u, m))
        sims.sort(reverse=True)
        sc = collections.Counter()
        for s, m in sims[:k]:
            for h in self.hints[m]:
                sc[h] += s
        if scores:
            return sc.most_common(topn)
        return [h for h, _ in sc.most_common(topn)]
