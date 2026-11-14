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
import argparse, collections, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loop, lemmas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('dir')
    ap.add_argument('--m', type=int, default=8, help='candidate assumptions per target')
    ap.add_argument('--sketch-time', type=float, default=5)
    ap.add_argument('--final-time', type=float, default=20)
    ap.add_argument('--runs', type=int, default=8, help='sketch runs per target (before the final run)')
    ap.add_argument('--side', default='both', choices=['both', 'below', 'after'])
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
    sketch = collections.defaultdict(list)   # original -> sketch hints (canonical pairs), oldest first
    seen = collections.defaultdict(set)
    lock = threading.Lock()
    out = open(os.path.join(c.dir, 'climb.tsv'), 'a')
    sf = open(os.path.join(c.dir, 'solved.tsv'), 'a')

    def candidates(t):
        o, k = lemmas.split(t)
        pr = lp.lemma_src.get(o, set())
        js = [j for j in allgoals.get(o, ()) if j != k and j not in pr
              and (c.side == 'both' or (c.side == 'below') == (j < k))]
        js.sort(key=lambda j: (abs(gl[f'{o}__goal_{j}'] - gl[t]), j))
        res = []
        for j in js:
            f = lemmas.conjecture(f'{o}__goal_{j}')
            if f and lemmas.unit_eq(f):   # (a conditional goal's statement is not an equation)
                res.append(j)
            if len(res) >= c.m:
                break
        return res

    def run(t, S, budget, tag):
        o, _ = lemmas.split(t)
        lp.extra_axioms[t] = [(f'assume_goal_{j}', lemmas.conjecture(f'{o}__goal_{j}')) for j in sorted(S)]
        with lock:
            hs = list(sketch[o])
        # sketch hints first: hints_for keeps the pool's order and a cap applies to the tail
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        n, ok, dt, stats, res = lp.run_one(t, hints, 1, budget, False, a_cpu(budget))
        lp.extra_axioms.pop(t, None)
        used = lp.used.pop(t, set()) if ok else set()
        U = {int(x[len('assume_goal_'):]) for x in used if x.startswith('assume_goal_')}
        if ok and res:
            with lock:
                for h in res:
                    if h not in seen[o]:
                        seen[o].add(h); sketch[o].append(h)
        with lock:
            out.write(f'{t}\t{tag}\t{len(S)}\t{"THM" if ok else "NO"}\t{len(U) if ok else -1}\t{dt:.2f}\t'
                      f'{",".join(map(str, sorted(S)))}\t{",".join(map(str, sorted(U)))}\t{len(hs)}\n')
            out.flush()
        return ok, U, res

    def a_cpu(b):
        return 10 * b

    def climb(t):
        S0 = candidates(t)
        queue = [frozenset(S0)] if S0 else []
        tried = set(); runs = 0; real = None
        bt = c.sketch_time; anyproof = False
        while queue and runs < c.runs:
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
                for u in sorted(U, key=lambda j: -abs(j - lemmas.split(t)[1])):
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
