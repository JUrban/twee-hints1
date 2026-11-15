#!/usr/bin/env python3
"""Prover9 on twee's frontier (15 Nov): a different search for goals that are stalled in twee.

For each goal, a LADR problem with prolog-style variables, so that TPTP names and twee's hints
need no translation:
  * assumptions: the TPTP axioms, and up to --lemmas proven siblings on either side (by goal
    number; their conjectures, as loop.py --lemma-after uses them);
  * goal: the conjecture;
  * hints: the proof steps of all solved goals of the same original (LOOPDIR/hints/<goal>, twee's
    generalised, skolem-free hints), deduplicated.
A proof is written as a twee hints file (its positive equations, variables renamed X0, X1, ...;
steps with the goal's skolem constants dropped: they came from the denial).

Batch mode: run NAMES against LOOPDIR's solved goals; proofs go to OUTDIR/hints/<goal> and a row
"<goal> 1 <seconds>" to OUTDIR/solved.tsv (merge.py moves them into the loop dir).
  python3 p9twee.py NAMES LOOPDIR OUTDIR [--timeout 60] [-j 2] [--lemmas 6]

Live mode: a side worker for a running loop.py (which reads rows that others append with --sync).
It takes the goals twee is stalled on (the latest round's last run of the goal failed and was not
fresh, and a fresh run in that round failed too), nearest to a proof first (proof lines), at most
--max-lgap lines away. A goal is tried again only when its nearest proven goal below changed or its
original's pool grew by --retry-grow. Proofs go straight into LOOPDIR (hints file, then a
solved.tsv row of the loop's current round).
  python3 p9twee.py --live LOOPDIR OUTDIR [-j 3] [--timeout 60]

Rows of OUTDIR/results.tsv: goal, THM/NO, seconds, Prover9 exit code (4 = time limit), hints,
lemmas (live mode adds the nearest proven goal below and the time).
"""
import argparse, collections, glob, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED

TPTP = '/project/AIM60k/problems/tptp'
GOAL_LINES = '/project/hintwork/abs/goal_lines.tsv'


def split(n):
    o, k = n.rsplit('__goal_', 1)
    return o, int(k)


def tptp_parts(name):
    txt = open(os.path.join(TPTP, name + '.p')).read()
    ax = [m.group(1).strip() for m in re.finditer(r'^cnf\(\w+,\s*axiom,\s*(.*)\)\.\s*$', txt, re.M)]
    m = re.search(r'fof\(\w+,\s*conjecture,\s*(.*)\)\.\s*$', txt, re.S)
    return ax, m.group(1).strip() if m else None


def ladr(f):
    """A TPTP formula as LADR text (prolog-style variables; free variables are universal)."""
    f = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', f).strip()
    f = f.replace('<=>', '<->').replace('=>', '->').replace('~', '-')
    return f


def twee_hint(eq):
    """A LADR equation 'l = r' (prolog-style variables) as a twee hints line 'l<TAB>r', variables X0..."""
    if ' = ' not in eq or '!=' in eq or re.search(r'\bc\d+\b', eq):
        return None   # (steps with the goal's skolem constants c1, c2, ... came from the denial)
    vs = {}
    def ren(m):
        v = m.group(0)
        if v not in vs:
            vs[v] = f'X{len(vs)}'
        return vs[v]
    l, r = eq.split(' = ', 1)
    l = re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', ren, l.strip()); r = re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', ren, r.strip())
    return f'{l}\t{r}'


_line = re.compile(r'^(\d+) (.*?)\.\s+\[(.*)\]\.\s*$')


def proof_eqs(out):
    i = out.find('= PROOF ='); j = out.find('= end of proof =')
    if i < 0 or j < 0:
        return []
    eqs = []
    for l in out[i:j].splitlines():
        m = _line.match(l.strip())
        if not m or m.group(3).startswith(('assumption', 'goal', 'deny')):
            continue
        body = re.sub(r'\s*#\s*label\([^)]*\)', '', m.group(2)).strip()
        if '|' in body or body.startswith('-') or '$F' in body:
            continue
        eqs.append(body)
    return eqs


class P9:
    """Prover9 problems from a loop dir's solved goals and pools."""
    def __init__(self, a):
        self.a = a
        self.byo = collections.defaultdict(set)
        self.pools = {}   # original -> (number of solved goals it was built from, hints)
        for d in ('in', 'out', 'hints'):
            os.makedirs(os.path.join(a.outdir, d), exist_ok=True)

    def update(self, solved):
        byo = collections.defaultdict(set)
        for n in solved:
            o, k = split(n); byo[o].add(k)
        self.byo = byo

    def pool(self, o):
        if o not in self.pools or self.pools[o][0] != len(self.byo[o]):
            hs = []; seen = set()
            for k in sorted(self.byo[o]):
                try:
                    for l in open(os.path.join(self.a.loopdir, 'hints', f'{o}__goal_{k}')):
                        if '\t' in l and l not in seen:
                            seen.add(l); hs.append(l.rstrip('\n').split('\t', 1))
                except OSError:
                    pass
            self.pools[o] = (len(self.byo[o]), hs)
        return self.pools[o][1]

    def problem(self, n):
        a = self.a
        o, k = split(n)
        ax, conj = tptp_parts(n)
        below = sorted(j for j in self.byo[o] if j < k)[-a.lemmas:] if a.lemmas else []
        above = sorted(j for j in self.byo[o] if j > k)[:a.lemmas] if a.lemmas else []
        lem = []
        for j in below + above:
            try:
                c = tptp_parts(f'{o}__goal_{j}')[1]
                if c:
                    lem.append(ladr(c))
            except OSError:
                pass
        hs = [] if a.no_hints else self.pool(o)
        txt = f'set(prolog_style_variables).\nclear(print_given).\nassign(max_seconds, {int(a.timeout)}).\n'
        if a.max_given:
            txt += f'assign(max_given, {a.max_given}).\n'
        txt += 'formulas(assumptions).\n' + ''.join(f'{x}.\n' for x in ax) + ''.join(f'{x}.\n' for x in lem) + 'end_of_list.\n'
        txt += f'formulas(goals).\n{ladr(conj)}.\nend_of_list.\n'
        if hs:
            txt += 'formulas(hints).\n' + ''.join(f'{l} = {r}.\n' for l, r in hs) + 'end_of_list.\n'
        return txt, len(hs), len(lem)

    def run(self, n):
        a = self.a
        txt, nh, nl = self.problem(n)
        p = os.path.join(a.outdir, 'in', n)
        open(p, 'w').write(txt)
        t0 = time.time(); rc = -1
        try:
            pr = subprocess.run([a.prover9, '-f', p], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=a.timeout * 3 + 30)
            out = pr.stdout.decode('utf8', 'replace'); rc = pr.returncode
        except subprocess.TimeoutExpired:
            out = ''
        dt = time.time() - t0
        ok = 'THEOREM PROVED' in out
        if ok:
            open(os.path.join(a.outdir, 'out', n), 'w').write(out)
        else:   # (inputs hold the whole pool, ~0.5 MB; keep only the proved ones)
            os.remove(p)
        hl = [h for h in (twee_hint(e) for e in proof_eqs(out)) if h] if ok else []
        return n, ok and bool(hl), dt, rc, nh, nl, hl


def read_solved(d):
    S, R = set(), 0
    for l in open(os.path.join(d, 'solved.tsv')):
        w = l.split('\t')
        if len(w) >= 2 and l.endswith('\n'):
            S.add(w[0]); R = max(R, int(w[1]))
    return S, R


def batch(a):
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    solved, _ = read_solved(a.loopdir)
    P = P9(a); P.update(solved)
    todo = [n for n in names if n not in solved]
    print(f'{len(todo)} of {len(names)} goals unsolved in {a.loopdir}', flush=True)
    with ThreadPoolExecutor(a.j) as ex, open(os.path.join(a.outdir, 'results.tsv'), 'a') as R, \
            open(os.path.join(a.outdir, 'solved.tsv'), 'a') as S:
        futs = [ex.submit(P.run, n) for n in todo]
        nok = 0
        for f in as_completed(futs):
            n, ok, dt, rc, nh, nl, hl = f.result()
            R.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{rc}\t{nh}\t{nl}\n'); R.flush()
            if ok:
                nok += 1
                open(os.path.join(a.outdir, 'hints', n), 'w').write(''.join(h + '\n' for h in hl))
                S.write(f'{n}\t1\t{dt:.2f}\n'); S.flush()   # (round 1: merge.py takes rows of round >= 1)
                print(f'PROVED {n} {dt:.1f}s hints={nh} lemmas={nl} steps={len(hl)}', flush=True)
        print(f'{nok}/{len(todo)} proved', flush=True)


def live(a):
    D = a.loopdir
    gl = {l.split()[0]: int(l.split()[1]) for l in open(GOAL_LINES)}
    P = P9(a)
    tried = {}   # goal -> (nearest proven goal below, pool size) at its last Prover9 run
    rpath = os.path.join(a.outdir, 'results.tsv')
    if os.path.exists(rpath):
        for l in open(rpath):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 8:
                tried[w[0]] = (w[6], int(w[4]))

    def below(n):
        o, k = split(n)
        b = [j for j in P.byo.get(o, ()) if j < k]
        return f'{o}__goal_{max(b)}' if b else ''

    def lgap(n):
        b = below(n)
        return gl[n] - gl[b] if b and n in gl and b in gl else 10 ** 6

    def stalled(S, busy):
        rfs = sorted(glob.glob(os.path.join(D, 'r*', 'results.tsv')), key=lambda p: int(p.split('/')[-2][1:]))
        last, fresh = {}, set()
        for l in open(rfs[-1]):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5:
                last[w[0]] = (w[1], w[4])
                if w[4] == 'L0':
                    fresh.add(w[0])
        res = []
        for n, (ok, lev) in last.items():
            if ok != 'NO' or lev == 'L0' or n not in fresh or n in S or n in busy or lgap(n) > a.max_lgap:
                continue
            if n in tried:
                b, h = tried[n]
                if b == below(n) and len(P.pool(split(n)[0])) < a.retry_grow * max(h, 1):
                    continue
            res.append(n)
        return sorted(res, key=lambda n: (lgap(n), n))

    t0 = time.time(); nok = 0; last_list = 0; todo = []
    with ThreadPoolExecutor(a.j) as ex, open(rpath, 'a') as R:
        running = {}
        while True:
            S, Rn = read_solved(D)
            P.update(S)
            if not todo or time.time() - last_list > 300:
                todo = stalled(S, set(running.values())); last_list = time.time()
                print(f'live: {len(todo)} stalled goals to try ({time.strftime("%T")})', flush=True)
            todo = [n for n in todo if n not in S and n not in running.values()]
            while len(running) < a.j and todo:
                n = todo.pop(0)
                tried[n] = (below(n), len(P.pool(split(n)[0])))
                running[ex.submit(P.run, n)] = n
            if not running:
                time.sleep(60); continue
            fin, _ = wait(list(running), timeout=30, return_when=FIRST_COMPLETED)
            for f in fin:
                running.pop(f)
                n, ok, dt, rc, nh, nl, hl = f.result()
                b, h = tried[n]
                R.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{rc}\t{nh}\t{nl}\t{b}\t{time.strftime("%T")}\n'); R.flush()
                S, Rn = read_solved(D)
                if ok and n not in S:
                    open(os.path.join(a.outdir, 'hints', n), 'w').write(''.join(x + '\n' for x in hl))
                    hp = os.path.join(D, 'hints', n)
                    open(hp + '.p9tmp', 'w').write(''.join(x + '\n' for x in hl))
                    os.replace(hp + '.p9tmp', hp)
                    with open(os.path.join(D, 'solved.tsv'), 'a') as sf:
                        sf.write(f'{n}\t{Rn}\t{dt:.2f}\n')
                    nok += 1
                    print(f'PROVED {n} {dt:.1f}s hints={nh} lemmas={nl} steps={len(hl)} total={nok} '
                          f'{time.time()-t0:.0f}s', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('args', nargs='+', help='NAMES LOOPDIR OUTDIR, or with --live: LOOPDIR OUTDIR')
    ap.add_argument('--live', action='store_true')
    ap.add_argument('--timeout', type=float, default=60)
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--lemmas', type=int, default=6)
    ap.add_argument('--max-given', type=int, default=0)
    ap.add_argument('--max-lgap', type=int, default=80)
    ap.add_argument('--retry-grow', type=float, default=1.25)
    ap.add_argument('--no-hints', action='store_true')
    ap.add_argument('--prover9', default='/project/bin/prover9-new')
    a = ap.parse_args()
    if a.live:
        a.loopdir, a.outdir = a.args
        live(a)
    else:
        a.names, a.loopdir, a.outdir = a.args
        batch(a)


if __name__ == '__main__':
    main()
