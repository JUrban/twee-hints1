#!/usr/bin/env python3
"""(20 Nov) exp39b: unsolved goals of the stronger theories run without their extra axioms (paired pilot).

Most originals are the 17 base axioms plus 1 or 2 hypotheses (67 with one more, 28 with two). An unsolved goal G0 of
such an original runs in two arms with the same lemmas and hints:
  * full: G0's problem as it is;
  * nax: the axioms outside the base set dropped.
Lemma axioms are the 6 proven goals just below G0 in its original and 30 random proven base goals. Both are theorems
of G0's theory, so a proof in either arm is a proof of G0 in its own theory. The siblings may carry what G0 needs
from the hypotheses, without the hypotheses' search. Hints: the pool of G0's original. Twee as production, T s.
Both arms' given rules are also scanned against the unsolved goals (axioms of G0's original within the goal's).

  naxrun.py OUTDIR [-n 60] [-T 20] [-j 2] [--seed 1]
writes OUTDIR/runs.tsv (goal, arm, THM/NO, wall s, rules, goals hit) and OUTDIR/direct/<arm>/<goal> sketches (proof
steps + lemma statements) for transfer.py run.
"""
import argparse, os, random, re, subprocess, sys, threading, time, zlib
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import given as givenlib, hintlib, lemmas
import gensat
from gensat import sig, axs, unit, SKEL, TWEE, L

lock = threading.Lock()
_pool = {}


def pool(o, S, names):
    if o not in _pool:
        h = {}
        for g in names:
            if lemmas.split(g)[0] == o and g in S:
                p = os.path.join(L, 'UL', 'hints', g)
                if os.path.exists(p):
                    h.update((x, None) for x in open(p) if '\t' in x)
        _pool[o] = list(h)
    return _pool[o]


def norm(line):
    return re.sub(r'\s+', '', line.split(',', 2)[2].rsplit(')', 1)[0])


def run(args):
    g0, arm, a, names = args
    st = gensat.st
    S, want = st['S'], st['want']
    base = axs('a_instances__goal_100')
    o, i0 = lemmas.split(g0)
    with lock:
        prov = sorted(lemmas.split(g)[1] for g in names if lemmas.split(g)[0] == o and g in S and unit(g))
        sib = [f'{o}__goal_{i}' for i in prov if i < i0][-6:]
        allp = [g for v in st['proven'].values() for _, g in v]
        rnd = random.Random(a.seed * 100003 + zlib.crc32(g0.encode()))
        lem = sib + [g for g in rnd.sample(allp, min(30, len(allp))) if g not in sib]
        hints = pool(o, S, names)
    d = os.path.join(a.out, 'tmp'); os.makedirs(d, exist_ok=True)
    pp = os.path.join(d, f'{arm}_{g0}.p'); hp = os.path.join(d, f'{arm}_{g0}.hints')
    lines = []
    for l in open(os.path.join(hintlib.PROB, g0 + '.p')):
        if arm == 'nax' and l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l and norm(l) not in base:
            continue
        lines.append(l)
    with open(pp, 'w') as f:
        f.write(''.join(lines).rstrip('\n') + '\n')
        f.writelines(f'fof(lemma_{j}, axiom, {lemmas.conjecture(g)}).\n' for j, g in enumerate(lem))
    with open(hp, 'w') as f:
        f.writelines(hints)
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
    sg = sig(g0)
    hit = set()
    for x in rules:
        if x is None or x[0] == x[1] or SKEL.sub('', x[0]) + '=' + SKEL.sub('', x[1]) not in st['skel']:
            continue
        for g in want.get(givenlib.key(x[0], x[1], sg), ()):
            if g != g0 and g not in S and axs(g0) <= axs(g):
                hit.add(g)
    if ok:
        pl, pg = hintlib.extract_hints(out)
        dd = os.path.join(a.out, 'direct', arm); os.makedirs(dd, exist_ok=True)
        with open(os.path.join(dd, g0), 'w') as f:
            f.writelines(f'{l}\t{r}\n' for l, r in pl + pg)
            for g in lem:
                u = unit(g)
                if u:
                    f.write(f'{u[1]}\t{u[2]}\n')
    with lock:
        with open(os.path.join(a.out, 'runs.tsv'), 'a') as f:
            f.write(f'{g0}\t{arm}\t{"THM" if ok else "NO"}\t{dt:.1f}\t{len(rules)}\t{len(hit)}\t{",".join(sorted(hit))}\n')
        print(f'{time.strftime("%H:%M:%S")} {g0} {arm} {"THM" if ok else "NO"} {dt:.0f}s {len(rules)} rules, '
              f'{len(hit)} goals hit', flush=True)
    for p in (pp, hp):
        try:
            os.unlink(p)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('-n', type=int, default=60)
    ap.add_argument('-T', type=int, default=20)
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    gensat.refresh(names)
    base = axs('a_instances__goal_100')
    cand = sorted(g for g in names if g not in gensat.st['S'] and unit(g) and base < axs(g))
    random.Random(a.seed).shuffle(cand)
    goals = cand[:a.n]
    with open(os.path.join(a.out, 'goals.tsv'), 'w') as f:
        f.writelines(g + '\n' for g in goals)
    print(f'{len(cand)} unsolved unit goals of theories with more than the base axioms; {len(goals)} -> both arms',
          flush=True)
    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(run, [(g, arm, a, names) for g in goals for arm in ('nax', 'full')]))
    R = {}
    for l in open(os.path.join(a.out, 'runs.tsv')):
        w = l.split('\t')
        R[(w[0], w[1])] = w[2] == 'THM'
    n = sum(R.get((g, 'nax'), False) for g in goals); f_ = sum(R.get((g, 'full'), False) for g in goals)
    print(f'naxrun: nax {n}, full {f_} of {len(goals)} {time.strftime("%H:%M:%S")}', flush=True)


if __name__ == '__main__':
    main()
