#!/usr/bin/env python3
"""exp34: the climber's conditional proofs (notes/2026-11-19-climber-outputs.md).

A sketch proof of target T that used only sibling assumptions U (climb.tsv: THM, U = goal_J, ...) says "T follows
from U within the sketch budget". When production has since proven every goal in U, T should follow with U as
lemmas, a real proof (U's proofs are real). Production does not do this: each run gets only its 6 nearest proven
siblings as lemmas.

Per ready target, three arms at the same budget, in the climber's production context (pool, rm4t, 6 sibling and 30
kNN lemmas, PG):
  A  plain (the control)
  B  + U's statements as lemma axioms
  C  B + the sketch proof's steps first in the hints (if its sketch file was saved)

condtest.py LIVE OUT [--budget 20] [-j 2] [--targets t1,t2,...] -- <loop.py options as abs/clhl2.sh's>
Reads LIVE/solved.tsv, LIVE/hints (read only) and every loops/*/climb.tsv; writes OUT/results.tsv.
"""
import argparse, collections, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import loop, lemmas

LOOPS = '/project/hintwork/loops'

def orig(n):
    return n.split('__goal_')[0]

def ready_targets(solved):
    """target -> (siblings, dir, tag): the smallest sibling-only assumption set of a sketch proof that used no
    true lemma, among the unsolved targets whose assumptions are all proven now"""
    best = {}
    for d in sorted(os.listdir(LOOPS)):
        p = os.path.join(LOOPS, d, 'climb.tsv')
        if not os.path.isfile(p):
            continue
        for l in open(p):
            f = l.rstrip('\n').split('\t')
            if len(f) < 10 or f[3] != 'THM' or ':weak' in f[1] or not f[7] or f[9] != '0':
                continue
            U = f[7].split(',')
            if not all(u.startswith('goal_') for u in U):
                continue
            t = f[0]
            S = tuple(sorted(f'{orig(t)}__goal_{u[5:]}' for u in U))
            if t in solved or not set(S) <= solved:
                continue
            sk = os.path.join(LOOPS, d, 'sketches', t, f[1])
            k = (len(S), not os.path.exists(sk))
            if t not in best or k < best[t][0]:
                best[t] = (k, S, d, f[1], sk if os.path.exists(sk) else None)
    return {t: v[1:] for t, v in best.items()}

def main():
    argv = sys.argv[1:]
    i = argv.index('--')
    ap = argparse.ArgumentParser()
    ap.add_argument('live'); ap.add_argument('out')
    ap.add_argument('--budget', type=float, default=20)
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--targets', default='')
    c = ap.parse_args(argv[:i])
    os.makedirs(c.out, exist_ok=True)
    if not os.path.exists(os.path.join(c.out, 'solved.tsv')):
        os.symlink(os.path.abspath(os.path.join(c.live, 'hints')), os.path.join(c.out, 'hints'))
        with open(os.path.join(c.out, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(c.live, 'solved.tsv')):
                w = l.split('\t')
                if len(w) >= 3 and l.endswith('\n'):
                    f.write(f'{w[0]}\t0\t{w[2].strip()}\n')
    a = loop.make_parser().parse_args(['/project/hintwork/sets/all', c.out] + argv[i + 1:])
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}; lp.capture_given = set(); lp.captured = {}
    solved = set(lp.solved)
    R = ready_targets(solved)
    if c.targets:
        R = {t: v for t, v in R.items() if t in c.targets.split(',')}
    print(f'{len(R)} ready targets', flush=True)
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    lock = threading.Lock()
    res = open(os.path.join(c.out, 'results.tsv'), 'a')
    def job(t, arm):
        S, d, tag, sk = R[t]
        hints = lp.hints_for(t, pools, None)
        name = t
        if arm in 'BC':
            lp_extra = [(f'lemma_cond_{s.split("__goal_")[1]}', lemmas.conjecture(s)) for s in S]
        else:
            lp_extra = []
        if arm == 'C' and sk:
            steps = [tuple(x.rstrip('\n').split('\t')[:2]) for x in open(sk) if not x.startswith('#')]
            seen = set(steps)
            hints = steps + [h for h in hints if tuple(h[:2]) not in seen]
        with lock:
            lp.extra_axioms[name] = lp_extra
        n, ok, dt, stats, _ = lp.run_one(name, hints, 1, c.budget, False, 10 * c.budget)
        with lock:
            lp.extra_axioms.pop(name, None)
            res.write(f'{t}\t{arm}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{",".join(S)}\t{d}/{tag}\t{stats}\n'); res.flush()
            print(t, arm, 'THM' if ok else 'NO', f'{dt:.1f}', flush=True)
    # (the arms of one target run one after another: lp.extra_axioms is keyed by the goal's name)
    def target(t):
        for arm in ('A', 'B', 'C') if R[t][3] else ('A', 'B'):
            job(t, arm)
    with ThreadPoolExecutor(c.j) as ex:
        list(ex.map(target, sorted(R)))

if __name__ == '__main__':
    main()
