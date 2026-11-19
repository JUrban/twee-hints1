#!/usr/bin/env python3
"""exp37's paired test of rule models, replayed as of each proof (notes/2026-11-19-retrained-models.md).

The first design (abs/mabrm.sh: one snapshot without all 400 test goals) broke the context. Today's 400 newest
proofs are long sibling chains in few originals, each goal proved with its just-proven predecessors as lemmas;
without them the rm4t control proved 2 of 122 at 20 s, where production had proved 99% within 20 s.
As exp36 (climbablate.py): each test goal runs in production's context as of its own proof, namely production's
solved rows before its row (loops/UL/solved.tsv is append-only), for the pool and the sibling lemmas. kNN lemmas
come from the goals before the first test goal's row. One arm (one model) per process, goals in row order.

modelreplay.py OUT NAMES BUDGET -- <loop.py options: --model --model-fixed M.bin,M.vocab --model-theory ...>
"""
import collections, os, sys
sys.path.insert(0, '/project/twee/hints')
import loop, lemmas

L = '/project/hintwork/loops'
UL = os.path.join(L, 'UL')

def orig(n):
    return n.split('__goal_')[0]

def main():
    argv = sys.argv[1:]
    i = argv.index('--')
    out, names, budget = argv[0], argv[1], float(argv[2])
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
    T = sorted((pos[t], t) for t in open(names).read().split() if t in pos)
    rp = os.path.join(out, 'results.tsv')
    done = set(l.split('\t')[0] for l in open(rp)) if os.path.exists(rp) else set()
    print(f'{len(T)} goals, {len(done)} done', flush=True)
    if a.model:
        lp.train_model(1)
        import rulemodel
        _, v_, gdir_ = lp.model
        voc_ = {}
        for line in open(v_):
            c_, k_ = line.rstrip('\n').split('\t'); voc_[k_] = int(c_)
        for _, t in T:
            if not os.path.exists(os.path.join(gdir_, t)):
                rulemodel.write_goalfile(t, voc_, os.path.join(gdir_, t))
    ctx0 = sorted(n for n, k in pos.items() if k < T[0][0] and n in full)
    lp.lemma_index = lemmas.LemmaIndex(ctx0, subsets=a.lemma_subsets)
    print(f'kNN lemma index over the {len(ctx0)} goals before the first test goal', flush=True)
    res = open(rp, 'a')
    for p_, t in T:
        if t in done:
            continue
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
        n, ok, dt, stats, _ = lp.run_one(t, base, 1, budget, False, 10 * budget)
        res.write(f'{t}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{len(base)}\t{stats}\n'); res.flush()
        print(t, 'THM' if ok else 'NO', f'{dt:.1f}', flush=True)

if __name__ == '__main__':
    main()
