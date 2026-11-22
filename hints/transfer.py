#!/usr/bin/env python3
"""Goals that are steps of existing proofs (16 Nov). An unsolved goal whose equation (up to variable names) is a
step of a proof of another goal with the same or weaker axioms is a theorem with its proof written down; the
production pool (--pool original) only offers the goal's own original's proofs, so most of these are never tried
with the proof that contains them.

  transfer.py find LOOPDIR --out GOALS.tsv [--any-theory]   # goal, source proofs, axioms beyond the goal's
  transfer.py run GOALS.tsv DIR [-j J] [--time T] [--src-lemmas K] -- LOOP-OPTIONS (--init SNAPSHOT ...)

`run` gives each goal its source proofs' steps first, then the usual pool, in one fresh run; proofs are written
to DIR (hints/, solved.tsv round 1) for merge.py.

  transfer.py live LOOPDIR DIR [-j J] [--time T] [--src-lemmas K] [--every S] -- LOOP-OPTIONS (no --init)

`live` repeats find (steps of proofs from the same or weaker axioms, instances of proven goals) and run on the new
candidates every S seconds beside a running loop, with LOOPDIR's proofs as context, and puts the proofs into it.
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
    unit = {}
    for f in os.listdir(hd):
        # only proofs of unconditional unit goals: a conditional goal's steps may use its hypotheses, and with
        # their constants generalized they can be false equations that match many goals
        o_ = f.rpartition('__goal_')[0]
        if f not in unit:
            try:
                unit[f] = lemmas.unit_eq(lemmas.conjecture(f) or '~')
            except OSError:
                unit[f] = False
        if not unit[f]:
            continue
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
    print(f'{len(hits)} unsolved goals are instances of steps of proofs of unit goals from the same or weaker axioms -> {out}')


def find_goal_instances(D, out, allp='/project/hintwork/sets/all'):
    """(find --goals) unsolved unit goals that are instances (or variants) of a proven unit goal of an original with
    the same or weaker axioms: provable in one step with that goal as a lemma (the --lemma-knn --lemma-subsets kind)"""
    S = [l.split('\t')[0] for l in open(os.path.join(D, 'solved.tsv'))]
    Sset = set(S)
    def unit_lits(n):
        try:
            lits = hintsel.goal_lits(n)
        except Exception:
            return None
        if len(lits) == 1 and lits[0][0]:
            l, r = key(lits[0][1], lits[0][2])
            return parse(l), parse(r)
        return None
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    byroot = {}
    for n in (l.strip() for l in open(allp)):
        if n and n not in Sset:
            u = unit_lits(n)
            if u:
                byroot.setdefault((root(u[0]), root(u[1])), []).append((n, u[0], u[1]))
                byroot.setdefault((root(u[1]), root(u[0])), []).append((n, u[1], u[0]))
    hits = {}
    for m in dict.fromkeys(S):
        try:
            if not lemmas.unit_eq(lemmas.conjecture(m) or '~'):
                continue
        except OSError:
            continue
        u = unit_lits(m)
        if not u:
            continue
        A = axs(m)
        for n, a, b in byroot.get((root(u[0]), root(u[1])), ()):
            if lemmas.split(n)[0] == lemmas.split(m)[0] or not A <= axs(n):
                continue
            sub = match(u[0], a, {})
            if sub is not False and match(u[1], b, sub) is not False:
                hits.setdefault(n, []).append(m)
    with open(out, 'w') as fo:
        for g, ms in sorted(hits.items()):
            fo.write(g + '\t' + ','.join(ms[:3]) + '\t1\n')
    print(f'{len(hits)} unsolved goals are instances of proven goals of other originals with the same or weaker '
          f'axioms -> {out}')


def find_same_other(D, out, allp='/project/hintwork/sets/all'):
    """(find --same-other, 16 Nov) unsolved unit goals whose statement (up to renaming) is a proven goal of an
    original whose axioms are NOT a subset of theirs (incomparable or stronger): 1,888 of 7,025 on 16 Nov. Such a
    proof holds for the goal if it (and its lemmas' proofs) use none of the missing axioms; run --src-pool tests
    that by proving the goal with the source original's whole pool as hints. Sources: fewest missing axioms first."""
    S = sorted({l.split('\t')[0] for l in open(os.path.join(D, 'solved.tsv'))}); Ss = set(S)
    def k(n):
        try:
            lits = hintsel.goal_lits(n)
        except Exception:
            return None
        return key(lits[0][1], lits[0][2]) if len(lits) == 1 and lits[0][0] else None
    pk = {}
    for n in S:
        x = k(n)
        if x:
            pk.setdefault(x, []).append(n)
    rows = []
    for g in (l.strip() for l in open(allp)):
        if not g or g in Ss:
            continue
        x = k(g)
        if not x or x not in pk:
            continue
        A = lemmas.axiom_set(g)
        fs = [f for f in pk[x] if not lemmas.axiom_set(f) <= A]
        if len(fs) < len(pk[x]):
            continue   # (a weaker source exists: find --goals has it)
        fs.sort(key=lambda f: (len(lemmas.axiom_set(f) - A), f))
        rows.append((len(lemmas.axiom_set(fs[0]) - A), g, fs[:3]))
    with open(out, 'w') as fo:
        for m, g, fs in sorted(rows, key=lambda r: (r[0], r[1])):
            fo.write(f'{g}\t{",".join(fs)}\t{m}\n')
    print(f'{len(rows)} unsolved goals are proven goals of originals with axioms not within theirs -> {out}')


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


def live(D, d, j, T, rest, src_lemmas, every, allp='/project/hintwork/sets/all'):
    """(live) beside a running loop D: every EVERY s, find the unsolved goals that are steps of D's proofs from the
    same or weaker axioms or instances of its proven goals, run the ones not tried with the same first source, and
    put the proofs into D (hints through DIR/hints -> D/hints, then a D/solved.tsv row, which D --sync takes in)"""
    import subprocess
    os.makedirs(d, exist_ok=True)
    if not os.path.lexists(os.path.join(d, 'hints')):
        os.symlink(os.path.abspath(os.path.join(D, 'hints')), os.path.join(d, 'hints'))
    me = os.path.abspath(__file__)
    while True:
        t0 = time.time()
        with open(os.path.join(d, 'solved.tsv.tmp'), 'w') as f:   # D's proofs as this dir's context (round 0)
            for l in open(os.path.join(D, 'solved.tsv')):
                w = l.split('\t')
                if len(w) >= 3 and l.endswith('\n'):
                    f.write(f'{w[0]}\t0\t{w[2].strip()}\n')
        os.replace(os.path.join(d, 'solved.tsv.tmp'), os.path.join(d, 'solved.tsv'))
        find(D, os.path.join(d, 'c_steps.tsv'), allp)          # (--set ALLP: only these goals are candidates)
        find_goal_instances(D, os.path.join(d, 'c_goals.tsv'), allp)
        tp = os.path.join(d, 'transfer.tsv')
        tried = set()
        if os.path.exists(tp):
            for l in open(tp):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 5:
                    tried.add((w[0], w[4].split(',')[0]))
        new = {}
        for c in ('c_goals.tsv', 'c_steps.tsv'):
            for l in open(os.path.join(d, c)):
                w = l.rstrip('\n').split('\t')
                if (w[0], w[1].split(',')[0]) not in tried and w[0] not in new:
                    new[w[0]] = l if l.endswith('\n') else l + '\n'
        with open(os.path.join(d, 'cycle.tsv'), 'w') as f:
            f.writelines(new.values())
        print(f'live: {len(new)} new candidates {time.strftime("%H:%M:%S")}', flush=True)
        if new:
            subprocess.run([sys.executable, me, 'run', os.path.join(d, 'cycle.tsv'), d, '-j', str(j), '--time', str(T),
                            '--src-lemmas', str(src_lemmas), '--live-dst', D, '--'] + rest)
        time.sleep(max(0, every - (time.time() - t0)))


USED_AX = re.compile(r'^Axiom \d+ \(([^)]*)\):', re.M)


def used_lemma_goals(proof, o):
    """(22 Nov 13:28, exp58b, notes/2026-11-22-src-used.md) the proven goals behind the lemma axioms a proof text used
    (its 'Axiom N (name):' lines; names as exp/trust.py resolves them; O is the proof's own original)"""
    out = []
    for x in USED_AX.findall(proof):
        m = re.match(r'lemma_goal_(\d+)$', x)
        if m:
            out.append(f'{o}__goal_{m.group(1)}'); continue
        m = re.match(r'(?:lemma_knn|srclem|skax)_\d+_(.+__goal_\d+)$', x)
        if m:
            out.append(m.group(1))
    return out


def run(goals, d, j, T, rest, src_lemmas=0, live_dst=None, src_pool=False, src_used=False):
    import loop
    os.makedirs(d, exist_ok=True)
    names = os.path.join(d, 'goals.names')   # (loop.py's goal set: names only)
    with open(names, 'w') as f:
        f.writelines(l.split('\t')[0] + '\n' for l in open(goals) if l.strip())
    a = loop.make_parser().parse_args([names, d] + rest)
    loop.init_dir(a)
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}
    lp.proof_dst = os.path.abspath(live_dst) if live_dst else None   # (20 Nov 15:03) the kept proofs go there too
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    src, rank = {}, {}
    tp = os.path.join(d, 'transfer.tsv')
    done = {l.split('\t')[0] for l in open(tp)} if os.path.exists(tp) and not live_dst else set()   # (a restart skips the tried)
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
            # (20 Nov) an absolute source is a sketch file (givenmatch.py: a derived rule's ancestry), named
            # DIR/<goal>/<loop>/<source name>; elsewhere its basename stands for the source goal
            for x in open(f if os.path.isabs(f) else os.path.join(hd, f)):
                w = tuple(x.rstrip('\n').split('\t')[:2])
                if len(w) == 2 and w not in seen:
                    seen.add(w); hs.append(w)
        if src_pool:   # (--src-pool) all proofs of the sources' originals, as hints (their lemma chains)
            for f in src[g]:
                for h in pools.get(lp.pool_key(os.path.basename(f)), []):
                    if (h[0], h[1]) not in seen:
                        seen.add((h[0], h[1])); hs.append((h[0], h[1]))
        n0 = len(hs)
        hs += [h for h in lp.hints_for(g, pools, None) if (h[0], h[1]) not in seen]
        if src_lemmas:
            # the source goals and their nearest proven goals below as lemma axioms (proven goals of the same or
            # weaker axioms: the kind --lemma-knn --lemma-subsets adds), which the source proofs had as axioms
            L, A = [], lemmas.axiom_set(g)
            for f in src[g]:
                o2, k2 = lemmas.split(os.path.basename(f))
                if not lemmas.axiom_set(os.path.basename(f)) <= A:
                    continue
                below = sorted((j for j in lp.lemma_src.get(o2, ()) if j <= k2), reverse=True)[:src_lemmas]
                for j in below:
                    m = f'{o2}__goal_{j}'
                    fm = lemmas.lemma_form(m)
                    if fm and (m, fm) not in L:
                        L.append((m, fm))
            # (20 Nov 10:35) named after their goal, so a kept output's USEDAXIOMS tells which (exp/trust.py)
            lp.extra_axioms[g] = [(f'srclem_{i}_{m}', fm) for i, (m, fm) in enumerate(L)]
        if src_used:
            # (22 Nov 13:28, --src-used, exp58b) the lemma axioms the source proofs used (their proof texts in
            # LIVE_DST/proofs, INIT/proofs or D/proofs), if proven here, not the goal and within the goal's axioms. A
            # proof's hint file has its derived steps only, so without these a transfer (a proof step, the same
            # statement in a stronger theory) has to re-derive the source's lemmas from hints.
            A = lemmas.axiom_set(g)
            have = {nm.split('_', 2)[2] for nm, _ in lp.extra_axioms.get(g, []) if nm.startswith('srclem_')}
            L2 = []
            pds = [os.path.join(x, 'proofs') for x in (live_dst, a.init, d) if x]
            for f in src[g]:
                b = os.path.basename(f)
                pf = next((os.path.join(x, b) for x in pds if os.path.exists(os.path.join(x, b))), None)
                if not pf:
                    continue
                for m in used_lemma_goals(open(pf).read(), lemmas.split(b)[0]):
                    if m != g and m in lp.solved and m not in have and lemmas.axiom_set(m) <= A:
                        fm = lemmas.lemma_form(m)
                        if fm:
                            have.add(m); L2.append((m, fm))
            k0 = len(lp.extra_axioms.get(g, []))
            lp.extra_axioms[g] = lp.extra_axioms.get(g, []) + [(f'srclem_{k0 + i}_{m}', fm) for i, (m, fm) in enumerate(L2)]
        # (20 Nov) a sketch file's .ax: the source run's axioms behind the sketch (givenmatch.py), as lemma axioms.
        # They are that run's axioms and lemmas (proven goals of the same or weaker axioms, pool hints as axioms).
        # (20 Nov 10:50) an optional third column names the proven goal the equation comes from (a step of its proof,
        # exp/stepjoin.py): the axiom is then skax_<i>_<goal>, which exp/trust.py resolves
        axr, seen_ax = [], set()
        for f in src[g]:
            if os.path.isabs(f) and os.path.exists(f + '.ax'):
                for x in open(f + '.ax'):
                    w = x.rstrip('\n').split('\t')
                    if len(w) >= 2 and (w[0], w[1]) not in seen_ax:
                        seen_ax.add((w[0], w[1])); axr.append((w[0], w[1], w[2] if len(w) > 2 and w[2] else None))
        if axr:
            fm = lambda l, r: ''.join(f'! [{v}] : ' for v in sorted(set(re.findall(r'\bX\d+\b', l + ' ' + r)))) + f'{l} = {r}'
            lp.extra_axioms[g] = lp.extra_axioms.get(g, []) + [(f'skax_{i}' + (f'_{sg}' if sg else ''), fm(l, r))
                                                               for i, (l, r, sg) in enumerate(axr)]
        n, ok, dt, stats, res = lp.run_one(g, hs, 1, T, False, 10 * T)
        lp.extra_axioms.pop(g, None)
        with lock:
            out.write(f'{g}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{n0}\t{",".join(src[g])}\n'); out.flush()
            if ok:
                with open(os.path.join(d, 'hints', g), 'w') as hf:
                    hf.writelines(f'{l}\t{r}\n' for l, r in res)
                sf.write(f'{g}\t1\t0\n'); sf.flush()
                if live_dst:   # (live) the row in the running loop's solved.tsv, at its current round
                    R = max(int(x.split('\t')[1]) for x in open(os.path.join(live_dst, 'solved.tsv'))
                            if x.count('\t') >= 2 and x.endswith('\n'))
                    with open(os.path.join(live_dst, 'solved.tsv'), 'a') as lf:
                        lf.write(f'{g}\t{R}\t0\n')
        return ok
    t0 = time.time()
    with ThreadPoolExecutor(j) as ex:
        r = list(ex.map(one, sorted(src, key=lambda g: rank[g])))
    print(f'transfer: {sum(r)}/{len(r)} {time.time()-t0:.0f}s')


def main():
    argv = sys.argv[1:]
    if argv[0] == 'live':
        i = argv.index('--') if '--' in argv else len(argv)
        opts, rest = argv[1:i], argv[i + 1:]
        val = lambda k, dflt: type(dflt)(opts[opts.index(k) + 1]) if k in opts else dflt
        live(opts[0], opts[1], val('-j', 2), val('--time', 20.0), rest, val('--src-lemmas', 6), val('--every', 1200.0),
             val('--set', '/project/hintwork/sets/all'))
        return
    if argv[0] == 'find' and '--same-other' in argv:
        find_same_other(argv[1], argv[argv.index('--out') + 1])
    elif argv[0] == 'find' and '--goals' in argv:
        find_goal_instances(argv[1], argv[argv.index('--out') + 1])
    elif argv[0] == 'find' and '--instances' in argv:
        find_instances(argv[1], argv[argv.index('--out') + 1])
    elif argv[0] == 'find':
        find(argv[1], argv[argv.index('--out') + 1], any_theory='--any-theory' in argv)
    else:
        i = argv.index('--') if '--' in argv else len(argv)
        opts, rest = argv[1:i], argv[i + 1:]
        goals, d = opts[0], opts[1]
        j = int(opts[opts.index('-j') + 1]) if '-j' in opts else 2
        T = float(opts[opts.index('--time') + 1]) if '--time' in opts else 20
        K = int(opts[opts.index('--src-lemmas') + 1]) if '--src-lemmas' in opts else 0
        dst = opts[opts.index('--live-dst') + 1] if '--live-dst' in opts else None
        run(goals, d, j, T, rest, K, dst, '--src-pool' in opts, '--src-used' in opts)


if __name__ == '__main__':
    main()
