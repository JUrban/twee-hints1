#!/usr/bin/env python3
"""Goals that are steps of existing proofs (16 Nov). An unsolved goal whose equation (up to variable names) is a
step of a proof of another goal with the same or weaker axioms is a theorem with its proof written down; the
production pool (--pool original) only offers the goal's own original's proofs, so most of these are never tried
with the proof that contains them.

  transfer.py find LOOPDIR --out GOALS.tsv [--any-theory]   # goal, source proofs, axioms beyond the goal's
  transfer.py run GOALS.tsv DIR [-j J] [--time T] -- LOOP-OPTIONS (as climb.py: --init SNAPSHOT ...)

`run` gives each goal its source proofs' steps first, then the usual pool, in one fresh run; proofs are written
to DIR (hints/, solved.tsv round 1) for merge.py.
"""
import os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, hintsel, lemmas


def key(l, r):
    sig = set(re.findall(r'[a-z]\w*', l + ' ' + r))
    a = hintlib.generalize(l, r, sig); b = hintlib.generalize(r, l, sig)
    return min(a, b)


def parse(s):
    """term string -> nested tuples (functor, args...); variables are strings starting with an upper-case letter"""
    toks = re.findall(r'[A-Za-z0-9_]+|[(),]', s)
    pos = 0
    def term():
        nonlocal pos
        t = toks[pos]; pos += 1
        if pos < len(toks) and toks[pos] == '(':
            pos += 1; args = []
            while True:
                args.append(term())
                if toks[pos] == ',':
                    pos += 1
                else:
                    pos += 1; break   # ')'
            return (t,) + tuple(args)
        return t if t[0].isupper() else (t,)
    return term()


def match(p, t, sub):
    """extend SUB so that p under it is t (one-way matching); False if impossible"""
    if isinstance(p, str):
        if p in sub:
            return sub if sub[p] == t else False
        sub[p] = t
        return sub
    if isinstance(t, str) or p[0] != t[0] or len(p) != len(t):
        return False
    for a, b in zip(p[1:], t[1:]):
        if match(a, b, sub) is False:
            return False
    return sub


def root(x):
    return '*' if isinstance(x, str) else x[0]


def find_instances(D, out, allp='/project/hintwork/sets/all'):
    """(find --instances) unsolved unit goals that are instances of a step of a proof from the same or weaker
    axioms (the step, as a theorem, proves them by instantiation)"""
    S = {l.split('\t')[0] for l in open(os.path.join(D, 'solved.tsv'))}
    goals = []
    for n in (l.strip() for l in open(allp)):
        if not n or n in S:
            continue
        try:
            lits = hintsel.goal_lits(n)
        except Exception:
            continue
        if len(lits) == 1 and lits[0][0]:
            l, r = key(lits[0][1], lits[0][2])
            goals.append((n, parse(l), parse(r)))
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    # goals by (root of lhs, root of rhs), both orientations
    byroot = {}
    for g in goals:
        byroot.setdefault((root(g[1]), root(g[2])), []).append((g, False))
        byroot.setdefault((root(g[2]), root(g[1])), []).append((g, True))
    hits = {}
    hd = os.path.join(D, 'hints')
    seen = set()
    for f in os.listdir(hd):
        A = axs(f)
        try:
            lines = open(os.path.join(hd, f)).read().splitlines()
        except OSError:
            continue
        for x in lines:
            w = x.split('\t')
            if len(w) < 2 or (w[0], w[1], f.rpartition('__goal_')[0]) in seen:
                continue
            seen.add((w[0], w[1], f.rpartition('__goal_')[0]))
            try:
                pl, pr = parse(w[0]), parse(w[1])
            except (IndexError, ValueError):
                continue
            keys = [(root(pl), root(pr))]
            for k in keys:
                for (g, swap) in byroot.get(k, ()):
                    n, gl_, gr_ = g
                    if n in hits and len(hits[n]) >= 3:
                        continue
                    if not A <= axs(n):
                        continue
                    a, b = (gr_, gl_) if swap else (gl_, gr_)
                    sub = match(pl, a, {})
                    if sub is not False and match(pr, b, sub) is not False:
                        hits.setdefault(n, set()).add(f)
    with open(out, 'w') as fo:
        for g, fs in sorted(hits.items()):
            fs = sorted(fs, key=lambda f: (lemmas.split(f)[0] != lemmas.split(g)[0], len(axs(f) - axs(g))))
            fo.write(g + '\t' + ','.join(fs[:3]) + f'\t{len(axs(fs[0]) - axs(g))}\n')
    print(f'{len(hits)} unsolved goals are instances of steps of proofs from the same or weaker axioms -> {out}')


def find(D, out, allp='/project/hintwork/sets/all', any_theory=False):
    S = {l.split('\t')[0] for l in open(os.path.join(D, 'solved.tsv'))}
    want = {}
    for n in (l.strip() for l in open(allp)):
        if not n or n in S:
            continue
        try:
            lits = hintsel.goal_lits(n)
        except Exception:
            continue
        if len(lits) == 1 and lits[0][0]:
            want.setdefault(key(lits[0][1], lits[0][2]), []).append(n)
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    hits = {}
    hd = os.path.join(D, 'hints')
    for f in os.listdir(hd):
        try:
            for x in open(os.path.join(hd, f)):
                w = x.rstrip('\n').split('\t')
                if len(w) >= 2 and (w[0], w[1]) in want:
                    for g in want[(w[0], w[1])]:
                        if any_theory or axs(f) <= axs(g):
                            hits.setdefault(g, set()).add(f)
        except OSError:
            pass
    with open(out, 'w') as fo:
        for g, fs in sorted(hits.items()):
            # own original's proofs first, then the fewest axioms beyond the goal's (--any-theory: a source with more
            # may hold a step true only there; its hints are inert then), then the shortest
            fs = sorted(fs, key=lambda f: (lemmas.split(f)[0] != lemmas.split(g)[0], len(axs(f) - axs(g)),
                                           sum(1 for _ in open(os.path.join(hd, f)))))
            fo.write(g + '\t' + ','.join(fs[:3]) + f'\t{len(axs(fs[0]) - axs(g))}\n')
    print(f'{len(hits)} unsolved goals are steps of proofs from ' + ('any theory' if any_theory else
          'the same or weaker axioms') + f' -> {out}')


def run(goals, d, j, T, rest):
    import loop
    os.makedirs(d, exist_ok=True)
    names = os.path.join(d, 'goals.names')   # (loop.py's goal set: names only)
    with open(names, 'w') as f:
        f.writelines(l.split('\t')[0] + '\n' for l in open(goals) if l.strip())
    a = loop.make_parser().parse_args([names, d] + rest)
    loop.init_dir(a)
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    src, rank = {}, {}
    tp = os.path.join(d, 'transfer.tsv')
    done = {l.split('\t')[0] for l in open(tp)} if os.path.exists(tp) else set()   # (a restart skips the tried)
    for i, l in enumerate(open(goals)):
        w = l.rstrip('\n').split('\t')
        if w[0] in lp.solved or w[0] in done:
            continue
        src[w[0]] = w[1].split(',')
        rank[w[0]] = (int(w[2]) if len(w) > 2 and w[2].isdigit() else 0, i)   # fewest extra axioms first
    hd = os.path.join(a.init or d, 'hints')
    lock = threading.Lock()
    sf = open(os.path.join(d, 'solved.tsv'), 'a')
    out = open(os.path.join(d, 'transfer.tsv'), 'a')
    def one(g):
        hs, seen = [], set()
        for f in src[g]:
            for x in open(os.path.join(hd, f)):
                w = tuple(x.rstrip('\n').split('\t')[:2])
                if len(w) == 2 and w not in seen:
                    seen.add(w); hs.append(w)
        n0 = len(hs)
        hs += [h for h in lp.hints_for(g, pools, None) if (h[0], h[1]) not in seen]
        n, ok, dt, stats, res = lp.run_one(g, hs, 1, T, False, 10 * T)
        with lock:
            out.write(f'{g}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{n0}\t{",".join(src[g])}\n'); out.flush()
            if ok:
                with open(os.path.join(d, 'hints', g), 'w') as hf:
                    hf.writelines(f'{l}\t{r}\n' for l, r in res)
                sf.write(f'{g}\t1\t0\n'); sf.flush()
        return ok
    t0 = time.time()
    with ThreadPoolExecutor(j) as ex:
        r = list(ex.map(one, sorted(src, key=lambda g: rank[g])))
    print(f'transfer: {sum(r)}/{len(r)} {time.time()-t0:.0f}s')


def main():
    argv = sys.argv[1:]
    if argv[0] == 'find' and '--instances' in argv:
        find_instances(argv[1], argv[argv.index('--out') + 1])
    elif argv[0] == 'find':
        find(argv[1], argv[argv.index('--out') + 1], any_theory='--any-theory' in argv)
    else:
        i = argv.index('--') if '--' in argv else len(argv)
        opts, rest = argv[1:i], argv[i + 1:]
        goals, d = opts[0], opts[1]
        j = int(opts[opts.index('-j') + 1]) if '-j' in opts else 2
        T = float(opts[opts.index('--time') + 1]) if '--time' in opts else 20
        run(goals, d, j, T, rest)


if __name__ == '__main__':
    main()
