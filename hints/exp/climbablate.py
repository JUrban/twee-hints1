#!/usr/bin/env python3
"""exp36: do the climbs' sketch hints help the climber's own final runs? (notes/2026-11-19-climb-ablation.md)

User, 17:20: "are you saying the hints from the climbs never help outside the climbs? ... presumably they helped inside
the climb". No climber proof was ever ablated. climb.py's 'direct' runs are no control: they come after a successful
final run, when its own proof steps are already among the sketch hints.

Per climber real proof T (climb directories that saved their sketches), two arms in parallel, the same budget (the
directory's final time) and context:
  P  the pool only
  S  the sketch steps saved before T's proof (same original, same directory, file mtime <= the proof's) that are not
     in the pool, first, then the pool (as climb.py orders them)
Neither arm has fill lemmas (they were not saved) or assumptions.
The context is production's as of T's proof: its solved rows before T's row (loops/UL/solved.tsv is append-only), for
the pool and the sibling lemmas. kNN lemmas come from the rows before the earliest target's row, so no later proof
leaks in. Today's binary for both arms (twee-pg61, PG 0.25).

climbablate.py OUT [--dirs CLH,...] [-n N] -- <loop.py options as abs/clhl2.sh's>
"""
import collections, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import loop, lemmas

L = '/project/hintwork/loops'
UL = os.path.join(L, 'UL')
BUDGET = {'CLU': 20}   # (final time per directory; the others ran at 160)

def orig(n):
    return n.split('__goal_')[0]

def sketch_steps(d, o, tm):
    out = []
    sd = os.path.join(L, d, 'sketches')
    if not os.path.isdir(sd):
        return out
    files = []
    for t2 in os.listdir(sd):
        if orig(t2) != o:
            continue
        for g in os.listdir(os.path.join(sd, t2)):
            p = os.path.join(sd, t2, g)
            if os.path.getmtime(p) <= tm:
                files.append((os.path.getmtime(p), p))
    seen = set()
    for _, p in sorted(files):   # (oldest first, as climb.py's sketch list)
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if not l.startswith('#') and len(w) >= 2 and (w[0], w[1]) not in seen:
                seen.add((w[0], w[1])); out.append((w[0], w[1]))
    return out

def main():
    argv = sys.argv[1:]
    i = argv.index('--')
    out = argv[0]
    dirs = 'CLH,CLHL,CLU,CLHL2,FUD2p,FUDs'
    nmax = 10 ** 9
    for j, x in enumerate(argv[:i]):
        if x == '--dirs':
            dirs = argv[j + 1]
        if x == '-n':
            nmax = int(argv[j + 1])
    os.makedirs(out, exist_ok=True)
    if not os.path.exists(os.path.join(out, 'solved.tsv')):
        os.symlink(os.path.join(UL, 'hints'), os.path.join(out, 'hints'))
        with open(os.path.join(out, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(UL, 'solved.tsv')):
                w = l.split('\t')
                if len(w) >= 3 and l.endswith('\n'):
                    f.write(f'{w[0]}\t0\t{w[2].strip()}\n')
    a = loop.make_parser().parse_args(['/project/hintwork/sets/all', out] + argv[i + 1:])
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}; lp.capture_given = set(); lp.captured = {}
    full = dict(lp.solved)
    pos = {}
    for k, l in enumerate(open(os.path.join(UL, 'solved.tsv'))):
        pos.setdefault(l.split('\t')[0], k)
    T = []
    for d in dirs.split(','):
        for l in open(os.path.join(L, d, 'solved.tsv')):
            w = l.split('\t')
            t = w[0]
            if w[1:2] != ['1'] or t not in pos or not os.path.exists(os.path.join(UL, 'hints', t)):
                continue
            hp = os.path.join(L, d, 'hints', t)
            tm = os.path.getmtime(hp if os.path.exists(hp) else os.path.join(UL, 'hints', t))
            T.append((pos[t], t, d, tm))
    T.sort()
    T = T[:nmax]
    done = set()
    rp = os.path.join(out, 'results.tsv')
    if os.path.exists(rp):
        done = {tuple(l.split('\t')[:2]) for l in open(rp)}
    print(f'{len(T)} targets, {len(done)} runs done', flush=True)
    if a.model:
        lp.train_model(1)
        # (loop.py writes rule-model goal files for unsolved goals only; every target here is solved)
        import rulemodel
        _, v_, gdir_ = lp.model
        voc_ = {}
        for line in open(v_):
            c_, k_ = line.rstrip('\n').split('\t'); voc_[k_] = int(c_)
        for _, t, _, _ in T:
            if not os.path.exists(os.path.join(gdir_, t)):
                rulemodel.write_goalfile(t, voc_, os.path.join(gdir_, t))
    p0 = T[0][0]
    ctx0 = sorted(n for n, k in pos.items() if k < p0 and n in full)
    lp.lemma_index = lemmas.LemmaIndex(ctx0, subsets=a.lemma_subsets)
    print(f'kNN lemma index over the {len(ctx0)} goals before the first target', flush=True)
    res = open(rp, 'a'); lock = threading.Lock()
    for p_, t, d, tm in T:
        o = orig(t)
        ctx = {n: full[n] for n, k in pos.items() if k < p_ and n in full}
        lp.solved = ctx
        lp.lemma_src = {o_: set(v) for o_, v in lemmas.by_original(ctx).items()}
        cnt = collections.Counter()
        for n in ctx:
            if orig(n) == o:
                for h in lp.hints_of(n):
                    cnt[(h[0], h[1])] += 1
        pools = {lp.pool_key(t): [h for h, _ in cnt.most_common()]}
        lp.pool_cnt = {lp.pool_key(t): cnt}
        base = lp.hints_for(t, pools, None)
        inpool = set((h[0], h[1]) for h in base)
        sk = [h for h in sketch_steps(d, o, tm) if h not in inpool]
        budget = BUDGET.get(d, 160)
        arms = {'P': base, 'S': sk + base}
        def job(arm):
            if (t, arm) in done:
                return
            n, ok, dt, stats, _ = lp.run_one(t, arms[arm], 1, budget, False, 10 * budget,
                                            variant=1 if arm == 'P' else 2)   # (own tmp files)
            with lock:
                res.write(f'{t}\t{arm}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{d}\t{budget}\t{len(sk)}\t{len(base)}\t{stats}\n')
                res.flush()
                print(t, arm, 'THM' if ok else 'NO', f'{dt:.1f}', f'sketch-only {len(sk)}', flush=True)
        # (the two arms of a target at once: they share its context, set above)
        with ThreadPoolExecutor(2) as ex:
            list(ex.map(job, arms))

if __name__ == '__main__':
    main()
