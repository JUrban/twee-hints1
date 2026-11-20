#!/usr/bin/env python3
"""(20 Nov) Cross-run joining, a feasibility check: do unsolved goals follow by rewriting alone with the proof steps
of proven goals in weaker theories?

The given-log scan (2al) finds unsolved goals that are, as a whole, rules other runs derived. This asks the weaker
question: is G's ground (skolemized) equation s = t joinable by ordered rewriting with the union of the proof steps
(production's hints files) of every proven goal whose original's axioms are within G's? Each such step is a theorem
of G's theory. Rewriting is on ground terms with a total order (size, then precedence, then arguments), each step
used in both directions (when the right side's variables occur on the left), so it terminates and is sound. Steps
of G's own original are included.

  joincheck.py OUT.tsv [-n 400] [--seed 1] [--steps 3000]
writes OUT.tsv: goal, joined (1/0), the normal forms' sizes, the steps used (source goal + step index), seconds.
"""
import argparse, collections, os, random, sys, time
sys.path.insert(0, '/project/twee/hints')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lemmas
from gensat import axs, unit

L = '/project/hintwork/loops'


def parse(s):
    """'m(X0,ld(e,X1))' -> ('m', 'X0', ('ld', ('e',), 'X1')); variables are str, applications tuples"""
    pos = 0

    def term():
        nonlocal pos
        i = pos
        while pos < len(s) and s[pos] not in '(),':
            pos += 1
        name = s[i:pos]
        if pos < len(s) and s[pos] == '(':
            pos += 1
            args = [term()]
            while s[pos] == ',':
                pos += 1
                args.append(term())
            assert s[pos] == ')'
            pos += 1
            return (name,) + tuple(args)
        return name if name[:1].isupper() else (name,)
    t = term()
    assert pos == len(s), s
    return t


def vars_(t, acc):
    if isinstance(t, str):
        acc.add(t)
    else:
        for a in t[1:]:
            vars_(a, acc)
    return acc


def size(t):
    return 1 if isinstance(t, str) else 1 + sum(size(a) for a in t[1:])


def gt(a, b):
    """a total order on ground terms: size, then root symbol name, then arguments left to right"""
    sa, sb = size(a), size(b)
    if sa != sb:
        return sa > sb
    if a[0] != b[0]:
        return a[0] > b[0]
    for x, y in zip(a[1:], b[1:]):
        if x != y:
            return gt(x, y)
    return False


def preorder(t):
    """the discrimination-tree key: symbols in preorder, '*' for a variable"""
    out = []

    def go(u):
        if isinstance(u, str):
            out.append('*')
        else:
            out.append((u[0], len(u) - 1))
            for a in u[1:]:
                go(a)
    go(t)
    return tuple(out)


class Index:
    def __init__(self):
        self.root = {}

    def add(self, lhs, item):
        node = self.root
        for k in preorder(lhs):
            node = node.setdefault(k, {})
        node.setdefault(None, []).append(item)

    def candidates(self, t):
        """items whose lhs may match the ground term t"""
        flat = []   # (key, end index of the subterm starting here)

        def go(u):
            i = len(flat)
            flat.append(None)
            for a in u[1:]:
                go(a)
            flat[i] = ((u[0], len(u) - 1), len(flat))
        go(t)
        out = []
        stack = [(self.root, 0)]
        while stack:
            node, i = stack.pop()
            if i == len(flat):
                out.extend(node.get(None, ()))
                continue
            k, end = flat[i]
            if '*' in node:
                stack.append((node['*'], end))
            if k in node:
                stack.append((node[k], i + 1))
        return out


def match(p, t, sub):
    if isinstance(p, str):
        if p in sub:
            return sub[p] == t
        sub[p] = t
        return True
    if p[0] != t[0] or len(p) != len(t):
        return False
    for a, b in zip(p[1:], t[1:]):
        if not match(a, b, sub):
            return False
    return True


def inst(t, sub):
    return sub[t] if isinstance(t, str) else (t[0],) + tuple(inst(a, sub) for a in t[1:])


class Rewriter:
    def __init__(self, eqs, limit):
        """EQS: (lhs, rhs, tag) parsed; each direction whose right side's variables occur on its left"""
        self.ix = Index(); self.nf = {}; self.limit = limit; self.n = 0; self.skip = None
        self.hyp = {}   # (--cond) ground rules of one goal's hypotheses: lhs -> rhs
        self.ix2 = None   # (--own-given) one goal's own rules: its failed run's given rules
        for l, r, tag in eqs:
            vl, vr = vars_(l, set()), vars_(r, set())
            if not isinstance(l, str) and vr <= vl:
                self.ix.add(l, (l, r, tag))
            if not isinstance(r, str) and vl <= vr and l != r:
                self.ix.add(r, (r, l, tag))

    def norm(self, t, used):
        """T's normal form (memoised with the steps used); adds the steps to USED"""
        key = t
        if key in self.nf:
            v, u = self.nf[key]
            used |= u
            return v
        u0 = set()
        while True:
            self.n += 1
            if self.n > self.limit:
                raise TimeoutError
            t2 = (t[0],) + tuple(self.norm(a, u0) for a in t[1:])
            if t2 in self.hyp:
                u0.add(('hyp', 0))
                t = self.hyp[t2]
                continue
            cands = self.ix.candidates(t2)
            if self.ix2 is not None:
                cands = cands + self.ix2.candidates(t2)
            for l, r, tag in cands:
                if tag[0] == self.skip:
                    continue
                sub = {}
                if match(l, t2, sub):
                    rt = inst(r, sub)
                    if gt(t2, rt):
                        u0.add(tag)
                        t = rt
                        break
            else:
                t = t2
                break
        self.nf[key] = (t, frozenset(u0))
        used |= u0
        return t


def split_top(s, sep):
    out, dep, i0 = [], 0, 0
    for i, c in enumerate(s):
        dep += (c == '(') - (c == ')')
        if dep == 0 and s.startswith(sep, i):
            out.append(s[i0:i].strip()); i0 = i + len(sep)
    out.append(s[i0:].strip())
    return out


def cond(g):
    """a goal '~ s = t | u = v' -> ((s, t), (u, v)), else None"""
    import re
    import p9twee
    try:
        f = p9twee.tptp_parts(g)[1]
    except Exception:
        return None
    if not f or f.count('~') != 1:
        return None
    f = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', f).strip()
    while f.startswith('(') and f.endswith(')'):   # (outer parentheses, when they enclose the whole formula)
        inner = f[1:-1]; dep = 0; ok = True
        for i, c in enumerate(inner):
            dep += (c == '(') - (c == ')')
            if dep < 0:
                ok = False; break
        if not ok:
            break
        f = inner.strip()
    parts = split_top(f, '|')
    if len(parts) != 2 or not parts[0].startswith('~'):
        return None
    h = split_top(parts[0][1:].strip().strip('()'), '=') if parts[0][1:].strip().startswith('(') else split_top(parts[0][1:].strip(), '=')
    c = split_top(parts[1], '=')
    if len(h) != 2 or len(c) != 2:
        return None
    return (h[0], h[1]), (c[0], c[1])


def ground(t, m):
    if isinstance(t, str):
        return m.setdefault(t, ('sk_' + t.lower(),))
    return (t[0],) + tuple(ground(a, m) for a in t[1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('-n', type=int, default=400)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--steps', type=int, default=3000)
    ap.add_argument('--trusted', help='only these goals\' proofs as the bank (exp/trust.py OUT.trusted)')
    ap.add_argument('--shard', default='0/1', help='I/N: every Nth sampled goal from the Ith')
    ap.add_argument('--cond', action='store_true',
                    help='the conditional goals (one hypothesis s = t): its ground sides, normalised, as one oriented '
                         'rule for that goal only')
    ap.add_argument('--banks', default='',
                    help='(20 Nov 12:38) more loops (under loops/, comma-separated) whose hints files add proof steps '
                         'of the same goals (tag LOOP:goal); only goals production solved (and trusted)')
    ap.add_argument('--own-given', default='',
                    help='DIR (loop.py --given-keep): each goal\'s own failed run\'s given rules join the bank for that '
                         'goal (tag own:<line>); only goals with a file there are checked')
    ap.add_argument('--control', action='store_true',
                    help='sample proven goals instead, without their own proof steps (the method\'s power)')
    a = ap.parse_args()
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    by_o = collections.defaultdict(list)
    for g in names:
        by_o[lemmas.split(g)[0]].append(g)
    oax = {o: frozenset(axs(gs[0])) for o, gs in by_o.items()}
    U = sorted(g for g in names if (g in S) == a.control and (cond(g) if a.cond else unit(g)))
    random.Random(a.seed).shuffle(U)
    U = U[:a.n]
    U.sort(key=lambda g: (sorted(oax[lemmas.split(g)[0]]), g))   # (one bank per theory)
    si, sn = (int(x) for x in a.shard.split('/'))
    U = U[si::sn]
    if a.own_given:
        U = [g for g in U if os.path.exists(os.path.join(a.own_given, g))]
    TR = {l.strip() for l in open(a.trusted) if l.strip()} if a.trusted else None
    BANKS = [x for x in a.banks.split(',') if x]
    print(f'{len(U)} {"proven" if a.control else "unsolved"} {"conditional" if a.cond else "unit"} goals sampled', flush=True)
    # steps per source original: key -> (lhs, rhs, (source goal, index)) from production's hints files
    steps = {}

    def load(o):
        if o not in steps:
            d = {}
            for g in by_o[o]:
                if g not in S or not unit(g) or (TR is not None and g not in TR):
                    continue   # (a conditional goal's proof uses its hypotheses: steps not valid in general)
                for bk in ['UL'] + BANKS:
                    p = os.path.join(L, bk, 'hints', g)
                    try:
                        lines = open(p).read().split('\n')
                    except OSError:
                        continue
                    src = g if bk == 'UL' else f'{bk}:{g}'
                    for i, x in enumerate(lines):
                        w = x.split('\t')
                        if len(w) >= 2 and (w[0], w[1]) not in d and (w[1], w[0]) not in d:
                            d[(w[0], w[1])] = (src, i)
            steps[o] = d
        return steps[o]
    rw_cache = {}
    import modelcheck as mcheck, p9twee
    mmodels, mcache = {}, {}
    with open(a.out, 'w') as fo:
        for k, g in enumerate(U):
            t0 = time.time()
            o = lemmas.split(g)[0]
            srcs = tuple(sorted(x for x in by_o if oax[x] <= oax[o]))
            if srcs not in rw_cache:
                eqs = {}
                for x in srcs:
                    for (l, r), tag in load(x).items():
                        eqs.setdefault((l, r), tag)
                for ax in oax[o]:   # the theory's own axioms ('l=r' with A, B, ... variables)
                    if '!=' not in ax:
                        dep = 0
                        for i, c in enumerate(ax):
                            dep += (c == '(') - (c == ')')
                            if c == '=' and dep == 0:
                                eqs.setdefault((ax[:i], ax[i + 1:]), ('axiom', 0))
                                break
                parsed = []
                # (20 Nov 12:52) hints files also hold printed goal terms that are not theorems (X0 = t(X0,X1) in Z4's
                # lra2aa 214; notes/2026-11-20-model-audit.md). Every false line the audit found had different
                # variables on its two sides, so those lines must hold in the theory's Mace4 models (verdicts cached
                # in loops/JOIN/modelcache/<theory>)
                key = mcheck.theory_key(p9twee.tptp_parts(g)[0])
                if key not in mmodels:
                    mmodels[key] = mcheck.read_models(os.path.join(L, 'MODELCHECK', 'models', key + '.out'))
                    mcache[key] = {}
                    cp = os.path.join(L, 'JOIN', 'modelcache', key)
                    if os.path.exists(cp):
                        for x in open(cp):
                            w = x.rstrip('\n').split('\t')
                            if len(w) == 3:
                                mcache[key][(w[0], w[1])] = w[2] == '1'
                newv = []
                nfalse = 0
                for (l, r), tag in eqs.items():
                    try:
                        pl, pr = parse(l), parse(r)
                    except (AssertionError, IndexError):
                        continue
                    if vars_(pl, set()) != vars_(pr, set()):
                        ok = mcache[key].get((l, r))
                        if ok is None:
                            try:
                                ok = mcheck.holds(pl, pr, mmodels[key]) is None
                            except KeyError:
                                ok = False
                            mcache[key][(l, r)] = ok; newv.append((l, r, ok))
                        if not ok:
                            nfalse += 1
                            continue
                    parsed.append((pl, pr, tag))
                if newv:
                    os.makedirs(os.path.join(L, 'JOIN', 'modelcache'), exist_ok=True)
                    with open(os.path.join(L, 'JOIN', 'modelcache', key), 'a') as f:
                        f.writelines(f'{l}\t{r}\t{int(ok)}\n' for l, r, ok in newv)
                if len(rw_cache) > 3:
                    rw_cache.clear()
                tb = time.time()
                rw_cache[srcs] = Rewriter(parsed, a.steps)
                print(f'  bank for {o}: {len(srcs)} source originals, {len(parsed)} equations ({nfalse} false in a '
                      f'model left out), index {time.time() - tb:.0f}s', flush=True)
            rw = rw_cache[srcs]
            rw.n = 0
            if a.control:
                rw.skip = g; rw.nf = {}
            used = set()
            m = {}
            if a.cond:
                (hl, hr), (ls, rs) = cond(g)
                rw.nf = {}; rw.hyp = {}
            else:
                _, ls, rs = unit(g)
            s_, t_ = ground(parse(ls), m), ground(parse(rs), m)
            if a.own_given:
                ix2 = Index(); n2 = 0
                for i, x in enumerate(open(os.path.join(a.own_given, g))):
                    w = x.rstrip('\n').split('\t')
                    try:
                        l2, r2 = parse(w[0]), parse(w[1])
                    except (AssertionError, IndexError):
                        continue
                    vl, vr = vars_(l2, set()), vars_(r2, set())
                    if not isinstance(l2, str) and vr <= vl:
                        ix2.add(l2, (l2, r2, ('own', i))); n2 += 1
                    if not isinstance(r2, str) and vl <= vr and l2 != r2:
                        ix2.add(r2, (r2, l2, ('own', i))); n2 += 1
                rw.ix2 = ix2; rw.nf = {}
            try:
                if a.cond:
                    h1, h2 = rw.norm(ground(parse(hl), m), used), rw.norm(ground(parse(hr), m), used)
                    if h1 != h2:
                        rw.hyp = {h1: h2} if gt(h1, h2) else {h2: h1}
                        rw.nf = {}
                ns_, nt_ = rw.norm(s_, used), rw.norm(t_, used)
                j = int(ns_ == nt_)
                info = f'{size(ns_)}\t{size(nt_)}'
            except (TimeoutError, RecursionError):
                j, info = -1, '-\t-'
            if a.cond:
                rw.nf = {}; rw.hyp = {}
            if a.own_given:
                rw.nf = {}; rw.ix2 = None
            dt = time.time() - t0
            fo.write(f'{g}\t{j}\t{info}\t{",".join(f"{x}:{i}" for x, i in sorted(used))}\t{dt:.1f}\n')
            fo.flush()
            if j == 1:
                print(f'{k} {g} JOINED with {len(used)} steps ({dt:.1f}s)', flush=True)
    R = [l.split('\t') for l in open(a.out)]
    print(f'joincheck: {sum(w[1] == "1" for w in R)} joined, {sum(w[1] == "-1" for w in R)} over the step limit, '
          f'of {len(R)}', flush=True)


if __name__ == '__main__':
    main()
