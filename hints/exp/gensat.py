#!/usr/bin/env python3
"""(20 Nov) exp39: base-theory runs as rule generators for the unsolved goals of every stronger theory.

13 originals (a_instances, Ka_eq_aK3, ...) share one axiom set, the 17 base axioms, which is within the axioms of
nearly every original: their rules hold for 3,001 of the 3,133 unsolved unit goals. Of the first 27 goals that
production's failed runs derived (loop.py --given-scan, 04:15-05:30), 19 came from base-original runs, which had
1.18 of production's 14.7 CPU h: about 16 goals per CPU h, against production's own 0.6 proofs.

Each job here is a run on an unsolved unit goal G0 of a base original:
  * G0's problem (the base axioms and G0 as conjecture);
  * lemma axioms: the 6 proven goals of G0's original just below it, and K random proven unit goals of the base
    originals (seeded per job; all are base theorems);
  * hints: the pool of G0's original (production's proof steps of its proven goals);
  * twee as production (twee-pg61 with PG 0.25, --abstract-time 2000), T s, --print-given-unsolved.
Its given rules are checked against the unsolved unit goals as loop.py --given-scan does (canonical keys of both
orientations, axioms of G0's original within the goal's). Hits go to loops/GSAT/<stamp>/given/G0 and
loops/GSAT/hits.tsv in loop.py's format; givenmatch.py live runs them. A proof of G0 itself goes to
loops/GSAT/direct/G0 (its proof steps and the lemma axioms, as hints) and a row of loops/GSAT/direct.tsv.

  gensat.py [-j 3] [-T 30] [-K 30] [--jobs N] [--seed 1]
"""
import argparse, os, random, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import given as givenlib, hintlib, hintsel, lemmas

L = '/project/hintwork/loops'
D = os.path.join(L, 'GSAT')
B = ('axcom Kproperties_1 aa_instances_4 aK1_eq_aK3 TLRproperties_2 aKperms_1 nil3_2K aK2rev nil4_19K Ka1_eq_Ka2 '
     'a_instances Ka_eq_aK3 aK2_eq_aK3_1243b').split()
SKEL = re.compile(r'\b[A-Z]\w*|\s')
TWEE = '/project/bin/twee-pg61'
lock = threading.Lock()
st = {'t': 0.0}
_sig, _ax, _unit, _tpool = {}, {}, {}, {}
BASE = 'a_instances__goal_100'   # (any goal of a base original: its axioms are the base set)


def sig(n):
    o = lemmas.split(n)[0]
    if o not in _sig:
        _sig[o] = hintlib.problem_signature(n)
    return _sig[o]


def axs(n):
    o = lemmas.split(n)[0]
    if o not in _ax:
        _ax[o] = lemmas.axiom_set(n)
    return _ax[o]


def unit(n):
    if n not in _unit:
        try:
            lits = hintsel.goal_lits(n)
            _unit[n] = lits[0] if len(lits) == 1 and lits[0][0] else None
        except Exception:
            _unit[n] = None
    return _unit[n]


def refresh(names):
    """(every 10 minutes) production's solved goals, the targets' keys, the pools of the base originals"""
    with lock:
        if time.time() - st['t'] < 600:
            return
        S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv')) if l.endswith('\n')}
        want = {}; known = set()
        for g in names:
            if not unit(g):
                continue
            _, l, r = unit(g)
            for k in (givenlib.key(l, r, sig(g)), givenlib.key(r, l, sig(g))):
                known.add(k)   # (a check: rules that are some goal's statement, solved or not)
                if g not in S:
                    want.setdefault(k, set()).add(g)
        skel = {SKEL.sub('', k[0]) + '=' + SKEL.sub('', k[1]) for k in want}
        pool, proven = {}, {}
        for g in names:
            o, i = lemmas.split(g)
            if o in B and g in S and unit(g):
                proven.setdefault(o, []).append((i, g))
                p = os.path.join(L, 'UL', 'hints', g)
                if os.path.exists(p):
                    pool.setdefault(o, {}).update((x, None) for x in open(p) if '\t' in x)
        bg = sorted(g for g in names if lemmas.split(g)[0] in B and g not in S and unit(g))
        random.Random(7).shuffle(bg)   # (spread over the 13 originals)
        bax = axs(BASE)
        tg = sorted(g for g in names if lemmas.split(g)[0] not in B and g not in S and unit(g) and bax < axs(g))
        random.Random(7).shuffle(tg)
        st['tgoals'] = tg
        st.update(t=time.time(), S=S, want=want, known=known, skel=skel, pool=pool, proven=proven, basegoals=bg)
        print(f'{time.strftime("%H:%M:%S")} refresh: {len(want)} target keys, {len(st["basegoals"])} unsolved base '
              f'goals, {sum(len(v) for v in proven.values())} proven base goals', flush=True)


def tpool(o, S, names):
    if o not in _tpool:
        h = {}
        for g in names:
            if lemmas.split(g)[0] == o and g in S:
                p = os.path.join(L, 'UL', 'hints', g)
                if os.path.exists(p):
                    h.update((x, None) for x in open(p) if '\t' in x)
        _tpool[o] = list(h)
    return _tpool[o]


def job(args):
    k, a, names = args
    refresh(names)
    if a.target:
        return job_target(k, a, names)
    with lock:
        S, want, skel, known = st['S'], st['want'], st['skel'], st['known']
        bg = st['basegoals']
        if not bg:
            return None
        g0 = bg[k % len(bg)]
        o, i0 = lemmas.split(g0)
        prov = st['proven'].get(o, [])
        sib = [g for _, g in sorted(x for x in prov if x[0] < i0)[-6:]]
        allp = [g for v in st['proven'].values() for _, g in v]
        rnd = random.Random(a.seed * 100003 + k)
        if a.knn:   # (06:40, exp39c) production's kNN lemmas: the K proven goals nearest to G0 (same or weaker axioms)
            lem = sib + [g for g in st['index'].select(g0, a.K, exclude=set(sib)) if g not in sib]
        else:
            lem = sib + [g for g in rnd.sample(allp, min(a.K, len(allp))) if g not in sib]
        hints = list(st['pool'].get(o, {}))
    tag = f'{a.tag}{k}_{g0}'
    tmp = os.path.join(D, 'tmp'); os.makedirs(tmp, exist_ok=True)
    pp = os.path.join(tmp, tag + '.p'); hp = os.path.join(tmp, tag + '.hints')
    with open(pp, 'w') as f:
        f.write(open(os.path.join(hintlib.PROB, g0 + '.p')).read().rstrip('\n') + '\n')
        f.writelines(f'fof(lemma_{j}, axiom, {lemmas.lemma_form(g)}).\n' for j, g in enumerate(lem))
    return finish(k, a, g0, g0, lem, hints, tag, pp, hp)


def job_target(k, a, names):
    """(06:45, exp39d) a run steered to an unsolved goal G0 of a stronger theory: the base axioms with G0 as
    conjecture, the K proven goals of the base (or weaker) theories nearest to G0's statement as lemma axioms, the
    pool of G0's original as hints. A proof is a proof of G0 (from base theorems); every rule is a base theorem."""
    with lock:
        S = st['S']
        tg = st['tgoals']
        if not tg:
            return None
        g0 = tg[k % len(tg)]
        u = unit(g0)
        lem = [g for g in st['index'].select(BASE, a.K, eq=(u[1], u[2])) if g in S]
        hints = tpool(lemmas.split(g0)[0], S, names)
    tag = f'{a.tag}{k}_{g0}'
    tmp = os.path.join(D, 'tmp'); os.makedirs(tmp, exist_ok=True)
    pp = os.path.join(tmp, tag + '.p'); hp = os.path.join(tmp, tag + '.hints')
    with open(pp, 'w') as f:
        f.writelines(x for x in open(os.path.join(hintlib.PROB, BASE + '.p')) if 'conjecture' not in x)
        f.writelines(x for x in open(os.path.join(hintlib.PROB, g0 + '.p')) if x.startswith('fof(') and 'conjecture' in x)
        f.writelines(f'fof(lemma_{j}, axiom, {lemmas.lemma_form(g)}).\n' for j, g in enumerate(lem))
    return finish(k, a, g0, BASE, lem, hints, tag, pp, hp)


def finish(k, a, g0, src, lem, hints, tag, pp, hp):
    """run twee on PP (hints HP), scan its rules; SRC: a goal of the run's theory (for the signature and axioms)"""
    with lock:
        S, want, skel, known = st['S'], st['want'], st['skel'], st['known']
    with open(hp, 'w') as f:
        f.writelines(hints)   # (production's format: lhs TAB rhs [TAB ...] lines)
    cmd = [TWEE, pp, '--max-time', str(a.T), '--no-colour', '--quiet', '--no-proof', '--print-hints',
           '--print-given', '--print-given-unsolved', '--abstract-time', '2000', '--no-eqhint-consider']
    if hints:
        cmd += ['--hints-file', hp]
    t0 = time.time()
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=a.T * 8 + 60,
                             env=dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100')).stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
    dt = time.time() - t0
    ok = 'HINTS-END' in out
    rules = givenlib.parse_given_parents(out)
    sg = sig(src)
    hits = []; nk = 0
    for idx, x in enumerate(rules):
        if x is None or x[0] == x[1]:
            continue
        nk += givenlib.key(x[0], x[1], sg) in known
        if SKEL.sub('', x[0]) + '=' + SKEL.sub('', x[1]) not in skel:
            continue
        for g in want.get(givenlib.key(x[0], x[1], sg), ()):
            if g != g0 and g not in S and axs(src) <= axs(g):
                hits.append((g, idx))
    stamp = f'{int(time.time() * 1000)}_{tag}'
    if hits:
        gd = os.path.join(D, stamp, 'given'); os.makedirs(gd, exist_ok=True)
        ax = set(givenlib.key(l, r, sg) for l, r in givenlib.axioms(g0, pp))
        with open(os.path.join(gd, g0), 'w') as f:
            for idx, x in enumerate(rules):
                if x is None or x[0] == x[1]:
                    continue
                kk = givenlib.key(x[0], x[1], sg)
                f.write(f'{-1 if kk in ax else 0}\t{idx}\t{kk[0]}\t{kk[1]}\t{x[2]}\t{x[3]}\n')
    if ok:
        pl, pg = hintlib.extract_hints(out)
        dd = os.path.join(D, 'direct'); os.makedirs(dd, exist_ok=True)
        with open(os.path.join(dd, g0), 'w') as f:
            f.writelines(f'{l}\t{r}\n' for l, r in pl + pg)
            for g in lem:
                u = unit(g)
                if u:
                    f.write(f'{u[1]}\t{u[2]}\n')
    with lock:
        if hits:
            with open(os.path.join(D, 'hits.tsv'), 'a') as f:
                f.writelines(f'{g}\tGSAT/{stamp}\t{g0}\t{idx}\t0\t0\n' for g, idx in hits)
        if ok:
            with open(os.path.join(D, 'direct.tsv'), 'a') as f:
                f.write(f'{g0}\t{os.path.join(D, "direct", g0)}\t0\n')
        new = sorted(set(g for g, _ in hits) - st.setdefault('seen', set()))
        st['seen'] |= set(new)
        with open(os.path.join(D, 'runs.tsv'), 'a') as f:
            f.write(f'{a.tag}{k}\t{g0}\t{"THM" if ok else "NO"}\t{dt:.1f}\t{len(rules)}\t{len(hits)}\t{len(new)}\t'
                    f'{len(lem)}\t{len(hints)}\t{nk}\n')
        print(f'{time.strftime("%H:%M:%S")} {k} {g0} {"THM" if ok else "NO"} {dt:.0f}s {len(rules)} rules ({nk} goal statements), '
              f'{len(set(g for g, _ in hits))} goals hit, {len(new)} new {new[:4]}', flush=True)
    for p in (pp, hp):
        try:
            os.unlink(p)
        except OSError:
            pass
    return len(new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-j', type=int, default=3)
    ap.add_argument('-T', type=int, default=30)
    ap.add_argument('-K', type=int, default=30)
    ap.add_argument('--jobs', type=int, default=120)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--knn', action='store_true', help='kNN lemmas (lemmas.LemmaIndex.select) instead of random ones')
    ap.add_argument('--target', action='store_true', help='runs steered to unsolved goals of stronger theories (exp39d)')
    ap.add_argument('--tag', default='', help='a prefix of the run numbers in runs.tsv and the hit stamps')
    a = ap.parse_args()
    os.makedirs(D, exist_ok=True)
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    refresh(names)
    if a.knn or a.target:
        t0 = time.time()
        st['index'] = lemmas.LemmaIndex(sorted(st['S']), subsets=True)
        print(f'lemma index {time.time() - t0:.0f}s', flush=True)
    with ThreadPoolExecutor(a.j) as ex:
        n = sum(x or 0 for x in ex.map(job, [(k, a, names) for k in range(a.start, a.start + a.jobs)]))
    print(f'gensat: {a.jobs} runs, {n} new goals hit {time.strftime("%H:%M:%S")}', flush=True)


if __name__ == '__main__':
    main()
