#!/usr/bin/env python3
"""Sketch climbing (Veroff's sketches as a search over sets of assumptions).

For a target goal T = X__goal_N, the candidate assumptions are the statements
of the M nearest unproven sibling goals (steps of the same Prover9 proof, so
true, but not yet proven by us), nearest in proof lines, on either side.

The climb starts at the top of the lattice (all candidates assumed) and goes
down. Each run is T with an assumption set S as extra axioms, plus the
production context (proven sibling lemmas, kNN lemmas, the original's hint
pool, the rule model) and the sketch hints collected so far for the original.
A proof tells which assumptions it used (USEDAXIOMS), U. Its steps become
sketch hints of the original (shared by its targets). Then the sets U minus
one element are queued (smallest first). A proof with no assumption is a real
proof of T. Unless one is found, the climb ends with a real run of T with all
sketch hints.

Assumptions only change the problems that produce hints. Hints only guide
the search, so the real proofs are sound.

climb.py SET DIR [--m M] [--sketch-time S] [--final-time F] [--runs R] [-j J]
         -- <loop.py options for the production context>
Writes DIR/climb.tsv (one line per run) and, for real proofs, DIR/solved.tsv
and DIR/hints/<goal> as loop.py does.
"""
import argparse, collections, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loop, lemmas


VAR = re.compile(r'\bX\d+\b')
_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[(),=]")


def short(x):
    return x[len('assume_'):]


def parse_term(toks, i):
    """(term, next index); a term is a variable name (capitalised) or (f, [args])."""
    t = toks[i]
    if i + 1 < len(toks) and toks[i + 1] == '(':
        args, i = [], i + 2
        while True:
            a, i = parse_term(toks, i)
            args.append(a)
            if toks[i] == ',':
                i += 1
            else:
                return (t, args), i + 1
    return (t if t[0].isupper() else (t, [])), i + 1


TWEE = '/project/bin/twee-e22'
_laws = {}
def laws(t):
    """Simplifying laws over the axioms' signature (Veroff's sketch assumptions, possibly false):
    commutativity of binary operations, associativity of the binary operations the axioms do not
    define, and each defined operation (an axiom f(X1..Xn) = s, distinct variables, f not in s)
    equal to a constant of the axioms or to its first argument."""
    path = os.path.join(lemmas.PROB, t + '.p')
    ar, consts, defined = {}, set(), set()
    for line in open(path):
        if not (line.startswith('cnf(') and ',axiom,' in line):
            continue
        body = line.split(',axiom,', 1)[1].rsplit(')', 1)[0]
        toks = _tok.findall(body)
        try:
            lhs, i = parse_term(toks, 0)
            rhs, _ = parse_term(toks, i + 1)
        except (IndexError, ValueError):
            continue
        def walk(x):
            if isinstance(x, tuple):
                ar[x[0]] = len(x[1])
                if not x[1]:
                    consts.add(x[0])
                for y in x[1]:
                    walk(y)
        walk(lhs); walk(rhs)
        def syms(x):
            return {x[0]} | set().union(*map(syms, x[1])) if isinstance(x, tuple) else set()
        if isinstance(lhs, tuple) and lhs[1] and all(isinstance(v, str) for v in lhs[1]) \
                and len(set(lhs[1])) == len(lhs[1]) and lhs[0] not in syms(rhs):
            defined.add(lhs[0])
    key = (tuple(sorted(ar.items())), tuple(sorted(consts)), tuple(sorted(defined)))
    if key in _laws:
        return _laws[key]
    res = {}
    for f, n in sorted(ar.items()):
        if n == 2:
            res[f'assume_law_comm_{f}'] = f'! [X,Y] : {f}(X,Y) = {f}(Y,X)'
            if f not in defined:
                res[f'assume_law_assoc_{f}'] = f'! [X,Y,Z] : {f}({f}(X,Y),Z) = {f}(X,{f}(Y,Z))'
        if f in defined and n >= 1:
            vs = ','.join(f'X{i}' for i in range(n))
            for e in sorted(consts):
                res[f'assume_law_{f}_is_{e}'] = f'! [{vs}] : {f}({vs}) = {e}'
            res[f'assume_law_{f}_is_x'] = f'! [{vs}] : {f}({vs}) = X0'
    # drop the laws that collapse the theory (prove X = Y with the axioms): with one of them
    # every sketch is trivial and its hints are worthless
    ax = ''.join(l for l in open(path) if l.startswith('cnf(') and ',axiom,' in l)
    keep = {}
    for lab, f in res.items():
        tmp = os.path.join('/tmp' if not os.environ.get('TMPDIR') else os.environ['TMPDIR'],
                           f'climb_collapse_{os.getpid()}_{lab}.p')
        with open(tmp, 'w') as fh:
            fh.write(ax + f'fof({lab}, axiom, {f}).\nfof(collapse, conjecture, ! [X,Y] : X = Y).\n')
        try:
            o = subprocess.run([TWEE, tmp, '--max-time', '2', '--abstract-time', '2000', '--quiet', '--no-proof'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120).stdout.decode()
        except subprocess.TimeoutExpired:
            o = ''
        os.unlink(tmp)
        if 'Theorem' not in o:
            keep[lab] = f
    print(f'laws: {len(keep)} of {len(res)} kept, collapsing: {sorted(short(x) for x in res if x not in keep)}', flush=True)
    _laws[key] = keep
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('dir')
    ap.add_argument('--m', type=int, default=8, help='candidate assumptions per target')
    ap.add_argument('--sketch-time', type=float, default=5)
    ap.add_argument('--final-time', type=float, default=20)
    ap.add_argument('--runs', type=int, default=8, help='sketch runs per target (before the final run)')
    ap.add_argument('--side', default='both', choices=['both', 'below', 'after'])
    ap.add_argument('--laws', action='store_true',
                    help='also assume simplifying laws (possibly false), as Veroff: commutativity and '
                         'associativity of binary operations, derived operations trivial')
    ap.add_argument('--freq', type=int, default=0,
                    help='also assume the K most frequent equations of the original\'s proofs (unconditional goals)')
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--goal-lines', default='/project/hintwork/abs/goal_lines.tsv')
    argv = sys.argv[1:]
    i = argv.index('--') if '--' in argv else len(argv)
    c = ap.parse_args(argv[:i])
    rest = argv[i + 1:]   # loop.py options for the production context
    a = loop.make_parser().parse_args([c.set, c.dir] + rest)
    loop.init_dir(a)
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}
    gl = {l.split()[0]: int(l.split()[1]) for l in open(c.goal_lines)}
    allgoals = lemmas.by_original(gl)
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    cands = {}
    # equation counts over the proofs of unconditional goals of the targets' originals (--freq):
    # a conditional goal's hypotheses become false 'hints' like X0 = X1 when generalised
    ucnt = collections.defaultdict(collections.Counter)
    if c.freq:
        keys = {lp.pool_key(t) for t in lp.names}
        for n in lp.solved:
            if '__goal_' in n and lp.pool_key(n) in keys:
                f = lemmas.conjecture(n)
                if f and lemmas.unit_eq(f):
                    ucnt[lp.pool_key(n)].update((h[0], h[1]) for h in lp.hints_of(n))
    sketch = collections.defaultdict(list)   # original -> sketch hints (canonical pairs), oldest first
    seen = collections.defaultdict(set)
    lock = threading.Lock()
    out = open(os.path.join(c.dir, 'climb.tsv'), 'a')
    sf = open(os.path.join(c.dir, 'solved.tsv'), 'a')

    def candidates(t):
        """label -> TPTP formula of each candidate assumption of target T."""
        o, k = lemmas.split(t)
        pr = lp.lemma_src.get(o, set())
        js = [j for j in allgoals.get(o, ()) if j != k and j not in pr
              and (c.side == 'both' or (c.side == 'below') == (j < k))]
        js.sort(key=lambda j: (abs(gl[f'{o}__goal_{j}'] - gl[t]), j))
        res = {}
        for j in js:
            if sum(1 for x in res if x.startswith('assume_goal_')) >= c.m:
                break
            f = lemmas.conjecture(f'{o}__goal_{j}')
            if f and lemmas.unit_eq(f):   # (a conditional goal's statement is not an equation)
                res[f'assume_goal_{j}'] = f
        if c.laws:
            res.update(laws(t))
        if c.freq:
            cnt = ucnt.get(lp.pool_key(t), collections.Counter())
            i = 0
            for (l, r), n in cnt.most_common():
                if i >= c.freq or n < 3:
                    break
                if VAR.fullmatch(l) and VAR.fullmatch(r):
                    continue   # X0 = X1 would collapse everything
                vs = sorted(set(VAR.findall(l + ' ' + r)), key=lambda v: int(v[1:]))
                res[f'assume_freq_{i}'] = (f'! [{",".join(vs)}] : ' if vs else '') + f'{l} = {r}'
                i += 1
        return res

    def run(t, S, budget, tag):
        o, _ = lemmas.split(t)
        cand = cands[t]
        lp.extra_axioms[t] = [(x, cand[x]) for x in sorted(S)]
        with lock:
            hs = list(sketch[o])
        # sketch hints first: hints_for keeps the pool's order and a cap applies to the tail
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        n, ok, dt, stats, res = lp.run_one(t, hints, 1, budget, False, a_cpu(budget))
        lp.extra_axioms.pop(t, None)
        used = lp.used.pop(t, set()) if ok else set()
        U = {x for x in used if x.startswith('assume_')}
        if ok and res:
            with lock:
                for h in res:
                    if h not in seen[o]:
                        seen[o].add(h); sketch[o].append(h)
        with lock:
            out.write(f'{t}\t{tag}\t{len(S)}\t{"THM" if ok else "NO"}\t{len(U) if ok else -1}\t{dt:.2f}\t'
                      f'{",".join(short(x) for x in sorted(S))}\t{",".join(short(x) for x in sorted(U))}\t{len(hs)}\n')
            out.flush()
        return ok, U, res

    def a_cpu(b):
        return 10 * b

    def climb(t):
        cands[t] = candidates(t)
        S0 = list(cands[t])
        queue = [frozenset(S0)] if S0 else []
        tried = set(); runs = 0; real = None
        bt = c.sketch_time; anyproof = False
        banned = set(); minU = None
        while runs < c.runs:
            if not queue and minU:
                # stuck at minU (no smaller set proves T): ban its assumptions and climb again from
                # the top without them, for proofs (and hints) that go another way
                banned |= minU; minU = None
                rest = frozenset(S0) - banned
                if rest and rest not in tried:
                    queue.append(rest)
            if not queue:
                break
            queue.sort(key=len)
            S = queue.pop(0)
            if S in tried:
                continue
            tried.add(S)
            ok, U, res = run(t, S, bt, f's{runs}')
            runs += 1
            if ok and not U:
                real = res; break
            if not ok and not anyproof:
                # even the top of the lattice is too hard: retry it with twice the time
                bt *= 2; tried.discard(S); queue.append(S)
            if ok:
                anyproof = True
                if minU is None or len(U) < len(minU):
                    minU = frozenset(U)
                # (laws first: they may be false; then the farthest siblings)
                for u in sorted(U, key=lambda x: (not x.startswith('assume_law_'),
                                                  -abs(int(x[12:]) - lemmas.split(t)[1]) if x.startswith('assume_goal_') else 0)):
                    queue.append(frozenset(U - {u}))
        if real is None:
            ok, U, res = run(t, frozenset(), c.final_time, 'final')
            if ok:
                real = res
        if real is not None:
            with lock:
                sf.write(f'{t}\t1\t0\n'); sf.flush()
                with open(os.path.join(c.dir, 'hints', t), 'w') as hf:
                    for l, r in real:
                        hf.write(f'{l}\t{r}\n')
        return t, real is not None, runs

    todo = [n for n in lp.names if n not in lp.solved]
    t0 = time.time(); nsolved = 0
    with ThreadPoolExecutor(c.j) as ex:
        for t, ok, runs in ex.map(climb, todo):
            nsolved += ok
            print(f'{t} {"THM" if ok else "NO"} sketch-runs={runs} total={nsolved} {time.time()-t0:.0f}s', flush=True)
    print(f'climb: {nsolved}/{len(todo)} {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
