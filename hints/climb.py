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
import hintlib, loop, lemmas


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


TWEE = '/project/bin/twee-e37'
_laws = {}
_laws_lock = threading.Lock()
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
    with _laws_lock:
        if key not in _laws:
            _laws[key] = _make_laws(path, ar, consts, defined)
        return _laws[key]


def _make_laws(path, ar, consts, defined):
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
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('dir')
    ap.add_argument('--m', type=int, default=8, help='candidate assumptions per target')
    ap.add_argument('--sketch-time', type=float, default=5)
    ap.add_argument('--final-time', type=float, default=20)
    ap.add_argument('--max-sketch-time', type=float, default=None,
                    help='cap of the doubled sketch budget (default 4 x --sketch-time); a top set that fails '
                         'at the cap ends the climb')
    ap.add_argument('--runs', type=int, default=8, help='sketch runs per target (before the final run)')
    ap.add_argument('--side', default='both', choices=['both', 'below', 'after'])
    ap.add_argument('--laws', action='store_true',
                    help='also assume simplifying laws (possibly false), as Veroff: commutativity and '
                         'associativity of binary operations, derived operations trivial')
    ap.add_argument('--freq', type=int, default=0,
                    help='also assume the K most frequent equations of the original\'s proofs (unconditional goals)')
    ap.add_argument('--knn', type=int, default=0,
                    help='also assume the K unproven goals of other originals (axioms a subset of the '
                         'target\'s) most similar to the target: lines of Prover9 proofs, so true')
    ap.add_argument('--fill', type=float, default=0,
                    help='Veroff\'s gap filling: after each sketch proof, one twee --multi-goal run of this '
                         'many seconds tries to prove the proof\'s lemmas that depend on the assumptions, without '
                         'them; the proven ones become axioms (true lemmas) of the later runs on the original\'s goals')
    ap.add_argument('--fill-max', type=int, default=40, help='dependent lemmas per --fill check')
    ap.add_argument('--true-max', type=int, default=60, help='true lemmas (from --fill) per original')
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--goal-lines', default='/project/hintwork/abs/goal_lines.tsv')
    argv = sys.argv[1:]
    i = argv.index('--') if '--' in argv else len(argv)
    c = ap.parse_args(argv[:i])
    rest = argv[i + 1:]   # loop.py options for the production context
    a = loop.make_parser().parse_args([c.set, c.dir] + rest)
    loop.init_dir(a)
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}
    gl = {l.split()[0]: int(l.split()[1]) for l in open(c.goal_lines)}
    allgoals = lemmas.by_original(gl)
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    cands = {}
    if c.knn:
        uidx = lemmas.LemmaIndex(sorted(n for n in gl if n not in lp.solved), subsets=True)
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
    true = collections.defaultdict(dict)     # original -> {TPTP formula: label} of lemmas --fill proved
    tkey = {}                                # (original, label) -> the true lemma as a canonical hint pair
    checked = collections.defaultdict(set)   # original -> dependent lemmas --fill tried
    fo = open(os.path.join(c.dir, 'fill.tsv'), 'a')
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
        if c.knn:
            with lock:
                near = uidx.select(t, c.knn, exclude={f'{o}__goal_{j}' for j in allgoals.get(o, ())})
            for i, m in enumerate(near):
                res[f'assume_knn_{i}'] = lemmas.conjecture(m)
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

    def run(t, S, budget, tag, with_true=True):
        o, _ = lemmas.split(t)
        cand = cands[t]
        with lock:
            tl = [(lab, f) for f, lab in true[o].items()] if with_true else []
        lp.extra_axioms[t] = tl + [(x, cand[x]) for x in sorted(S)]
        with lock:
            hs = list(sketch[o])
        # sketch hints first: hints_for keeps the pool's order and a cap applies to the tail
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        n, ok, dt, stats, res = lp.run_one(t, hints, 1, budget, False, a_cpu(budget))
        lp.extra_axioms.pop(t, None)
        used = lp.used.pop(t, set()) if ok else set()
        deps = lp.assumed.pop(t, [])
        U = {x for x in used if x.startswith('assume_')}
        ut = sorted(x for x in used if x.startswith('true_'))
        nt = len(ut)
        if ok:
            last_true[t] = [tkey[(o, x)] for x in ut if (o, x) in tkey]
        if ok and res:
            with lock:
                for h in res:
                    if h not in seen[o]:
                        seen[o].add(h); sketch[o].append(h)
        with lock:
            out.write(f'{t}\t{tag}\t{len(S)}\t{"THM" if ok else "NO"}\t{len(U) if ok else -1}\t{dt:.2f}\t'
                      f'{",".join(short(x) for x in sorted(S))}\t{",".join(short(x) for x in sorted(U))}\t{len(hs)}\t{nt}\n')
            out.flush()
        if ok and U and c.fill:
            fill(t, deps, tag)
        return ok, U, res, nt

    def fill(t, deps, tag):
        """Veroff's gap filling: prove the sketch proof's assumption-dependent lemmas without the
        assumptions (with the true lemmas so far and the sketch hints); the proven ones become
        true lemmas of the original."""
        o, _ = lemmas.split(t)
        with lock:
            todo = []
            for asm, (l, r) in deps:
                vs = sorted(set(VAR.findall(l + ' ' + r)) | set(re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', l + ' ' + r)))
                f = (f'! [{",".join(vs)}] : ' if vs else '') + f'{l} = {r}'
                if f in true[o] or f in checked[o]:
                    continue
                checked[o].add(f); todo.append((l, r, vs, f))
            todo = todo[:c.fill_max]
            tl = list(true[o].items())
            hs = list(sketch[o])
        if not todo:
            return
        path = os.path.join(lemmas.PROB, t + '.p')
        lines = [x for x in open(path) if x.startswith(('cnf(', 'fof(')) and 'conjecture' not in x]
        if (a.lemmas or a.lemma_knn) and lp.lemma_src:
            # the target's lemmas (proven siblings, kNN goals), as in its own runs
            if a.lemma_knn:
                txt, _ = lemmas.lemma_problem_knn(t, lp.lemma_src, a.lemmas, lp.lemma_index, a.lemma_knn, a.lemma_after)
            else:
                txt, _ = lemmas.lemma_problem(t, lp.lemma_src, a.lemmas, a.lemma_after)
            lines += [x + '\n' for x in txt.splitlines() if x.startswith('fof(lemma_')]
        lines += [f'fof({lab}, axiom, {f}).\n' for f, lab in tl]
        for i, (l, r, vs, f) in enumerate(todo):
            sub = {v: f'skd{i}_{v.lower()}' for v in vs}
            g = lambda x: re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', lambda m: sub[m.group(0)], x)
            lines.append(f'cnf(dep_{i}, negated_conjecture, {g(l)} != {g(r)}).\n')
        tmp = os.path.join(c.dir, 'tmp', f'{t}.fill.p')
        with open(tmp, 'w') as fh:
            fh.writelines(lines)
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        hp = tmp + '.hints'
        with open(hp, 'w') as fh:
            for h in hints:
                fh.write('\t'.join(h) + '\n')
        cmd = [a.twee, tmp, '--max-time', str(c.fill), '--no-colour', '--quiet', '--no-proof', '--print-hints',
               '--multi-goal', '--hints-file', hp, '--max-cpu', str(a_cpu(c.fill))] + a.args.split()
        if lp.model:
            m, v, gdir = lp.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, t)] + a.model_args.split()
        t0 = time.time()
        try:
            o_ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=c.fill * a.wall_factor + 30).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            o_ = (e.stdout or b'').decode('utf8', 'replace')
        dt = time.time() - t0
        got = {line.split()[1] for line in o_.splitlines() if line.startswith('SOLVEDGOAL ')}
        new = []
        sig = lp.signature(t)
        with lock:
            for i, (l, r, vs, f) in enumerate(todo):
                if f'dep_{i}' in got and f not in true[o] and len(true[o]) < c.true_max:
                    true[o][f] = f'true_{len(true[o])}'; new.append(f)
                    tkey[(o, true[o][f])] = loop.canon_key(l, r, sig)
            if got and 'HINTS-END' in o_:
                L, G = hintlib.extract_hints(o_)
                for l, r in L + G:
                    if 'skd' in l or 'skd' in r:
                        continue
                    k = loop.canon_key(l, r, sig)
                    if k[0] != k[1] and k not in seen[o]:
                        seen[o].add(k); sketch[o].insert(0, k)   # real hints before the sketch's
            fo.write(f'{t}\t{tag}\t{len(deps)}\t{len(todo)}\t{len(got)}\t{len(new)}\t{len(true[o])}\t{dt:.2f}\n')
            fo.flush()
        for x in (tmp, hp):
            os.unlink(x)

    cap = c.max_sketch_time or 4 * c.sketch_time

    last_true = {}   # target -> the true lemmas its last proof used (canonical pairs)

    def a_cpu(b):
        return 10 * b

    def climb(t):
        cands[t] = candidates(t)
        S0 = list(cands[t])
        queue = [frozenset(S0)] if S0 else []
        tried = set(); runs = 0; real = None
        bt = c.sketch_time; anyproof = False
        banned = set(); minU = None; nt = 0
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
            ok, U, res, nt = run(t, S, bt, f's{runs}')
            runs += 1
            if ok and not U:
                real = res; break
            if not ok and not anyproof:
                # even the top of the lattice is too hard: retry it with twice the time, up to the cap
                if bt * 2 > cap:
                    break
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
            ok, U, res, nt = run(t, frozenset(), c.final_time, 'final')
            if ok:
                real = res
        direct = real is not None and not nt
        if real is not None and nt:
            # a proof with true lemmas (--fill): also try one without them, with all the hints
            ok, _, res, _ = run(t, frozenset(), c.final_time, 'direct', with_true=False)
            if ok:
                direct = True; real = res
        if real is not None:
            with lock:
                sf.write(f'{t}\t1\t0\n'); sf.flush()
                if not direct:
                    out.write(f'{t}\tchain\t0\tTHM\t0\t0\t\t\t0\t{nt}\n'); out.flush()
                with open(os.path.join(c.dir, 'hints', t), 'w') as hf:
                    # (a chain proof: the true lemmas it used are hints too)
                    for l, r in list(real) + ([] if direct else [k for k in last_true.get(t, []) if k not in real]):
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
