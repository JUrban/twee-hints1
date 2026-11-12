"""ENIGMA-style ("enigmatic") features of unit equations.

Follows E's che_enigmaticvectors.c, restricted to positive unit equalities:
  V  vertical walks of length 1..3 from the '=' root (variables as '*')
  H  horizontal: f.head(arg1)...head(argn)
  C  symbol counts
  D  symbol max depths
  L  length statistics, variable histogram
Features are returned as {name: value}; blocks get a prefix (e.g. 'h:' for
the hint, 'g:' for the goal) so they can be concatenated as in ENIGMA's
C+G blocks.
"""
import collections
from feats import parse, isvar

def _sym(t):
    return '*' if isvar(t) else t[0]

def features(l, r, vlen=3):
    f = collections.Counter()
    depth = collections.Counter()
    varocc = collections.Counter()
    st = {'len': 1, 'depth': 0, 'width': 0}

    def walk(t, path, d):
        s = _sym(t)
        path = path + [s]
        st['len'] += 1
        if isvar(t):
            varocc[t[0]] += 1
        if not t[1]:
            st['width'] += 1
            st['depth'] = max(st['depth'], d)
        else:
            f['H' + s + '.' + '.'.join(_sym(a) for a in t[1])] += 1
            for a in t[1]:
                walk(a, path, d + 1)
        for k in range(2, vlen + 1):
            if len(path) >= k:
                f['V' + '|'.join(path[-k:])] += 1
        if not isvar(t):
            f['C' + s] += 1
            depth[s] = max(depth[s], d)

    tl, tr = parse(l), parse(r)
    walk(tl, ['='], 1)
    walk(tr, ['='], 1)
    f['H=.' + '.'.join(sorted([_sym(tl), _sym(tr)]))] += 1
    for s, d in depth.items():
        f['D' + s] = d
    f['Llen'] = st['len']; f['Ldepth'] = st['depth']; f['Lwidth'] = st['width']
    f['Lvars'] = len(varocc); f['Lvocc'] = sum(varocc.values())
    f['Lvuniq'] = sum(1 for c in varocc.values() if c == 1)
    f['Lvshared'] = sum(1 for c in varocc.values() if c > 1)
    f['Lfuncs'] = sum(1 for k in depth)
    f['Lfocc'] = st['len'] - 1 - f['Lvocc']
    f['Lsizediff'] = abs(_size(tl) - _size(tr))
    f['Lvarside'] = 1 if (isvar(tl) or isvar(tr)) else 0
    return f

def _size(t):
    return 1 + sum(_size(a) for a in t[1])

class Vocab:
    """Maps feature names to column indices (no hashing collisions)."""
    def __init__(self):
        self.idx = {}
        self.frozen = False

    def get(self, k):
        i = self.idx.get(k)
        if i is None and not self.frozen:
            i = self.idx[k] = len(self.idx)
        return i
