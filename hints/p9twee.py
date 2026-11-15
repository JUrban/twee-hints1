#!/usr/bin/env python3
"""Prover9 on twee's frontier (15 Nov): a different search for goals that are stalled in twee.

For each goal, a LADR problem with prolog-style variables, so that TPTP names and twee's hints
need no translation:
  * assumptions: the TPTP axioms, and up to --lemmas proven siblings on either side (by goal
    number; their conjectures, as loop.py --lemma-after uses them);
  * goal: the conjecture;
  * hints: the proof steps of all solved goals of the same original (LOOPDIR/hints/<goal>, twee's
    generalised, skolem-free hints), deduplicated.
A proof is written back as a twee hints file (OUTDIR/hints/<goal>: its positive equations, variables
renamed X0, X1, ...; steps with the goal's skolem constants dropped), and a row "<goal> 1 <seconds>" goes to OUTDIR/solved.tsv, so that merge.py can
move it into the loop dir. Rows of OUTDIR/results.tsv: goal, THM/NO, seconds, Prover9 exit code (4 = time
limit), hints, lemmas.

  python3 p9twee.py NAMES LOOPDIR OUTDIR [--timeout 60] [-j 2] [--lemmas 6] [--max-given N]
"""
import argparse, collections, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TPTP = '/project/AIM60k/problems/tptp'


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('loopdir'); ap.add_argument('outdir')
    ap.add_argument('--timeout', type=float, default=60)
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--lemmas', type=int, default=6)
    ap.add_argument('--max-given', type=int, default=0)
    ap.add_argument('--no-hints', action='store_true')
    ap.add_argument('--prover9', default='/project/bin/prover9-new')
    a = ap.parse_args()
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    solved = set(l.split('\t')[0] for l in open(os.path.join(a.loopdir, 'solved.tsv')))
    byo = collections.defaultdict(set)
    for n in solved:
        o, k = split(n); byo[o].add(k)
    os.makedirs(os.path.join(a.outdir, 'in'), exist_ok=True); os.makedirs(os.path.join(a.outdir, 'out'), exist_ok=True)
    os.makedirs(os.path.join(a.outdir, 'hints'), exist_ok=True)
    pools = {}
    def pool(o):
        if o not in pools:
            hs = []; seen = set()
            for k in sorted(byo[o]):
                try:
                    for l in open(os.path.join(a.loopdir, 'hints', f'{o}__goal_{k}')):
                        if '\t' in l and l not in seen:
                            seen.add(l); hs.append(l.rstrip('\n').split('\t', 1))
                except OSError:
                    pass
            pools[o] = hs
        return pools[o]
    todo = [n for n in names if n not in solved]
    print(f'{len(todo)} of {len(names)} goals unsolved in {a.loopdir}', flush=True)
    for o in set(split(n)[0] for n in todo):
        pool(o)

    def run(n):
        o, k = split(n)
        ax, conj = tptp_parts(n)
        below = sorted(j for j in byo[o] if j < k)[-a.lemmas:] if a.lemmas else []
        above = sorted(j for j in byo[o] if j > k)[:a.lemmas] if a.lemmas else []
        lem = []
        for j in below + above:
            try:
                c = tptp_parts(f'{o}__goal_{j}')[1]
                if c:
                    lem.append(ladr(c))
            except OSError:
                pass
        hs = [] if a.no_hints else pool(o)
        txt = f'set(prolog_style_variables).\nclear(print_given).\nassign(max_seconds, {int(a.timeout)}).\n'
        if a.max_given:
            txt += f'assign(max_given, {a.max_given}).\n'
        txt += 'formulas(assumptions).\n' + ''.join(f'{x}.\n' for x in ax) + ''.join(f'{x}.\n' for x in lem) + 'end_of_list.\n'
        txt += f'formulas(goals).\n{ladr(conj)}.\nend_of_list.\n'
        if hs:
            txt += 'formulas(hints).\n' + ''.join(f'{l} = {r}.\n' for l, r in hs) + 'end_of_list.\n'
        p = os.path.join(a.outdir, 'in', n)
        open(p, 'w').write(txt)
        t0 = time.time()
        rc = -1
        try:
            pr = subprocess.run([a.prover9, '-f', p], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=a.timeout * 3 + 30)
            out = pr.stdout.decode('utf8', 'replace'); rc = pr.returncode
        except subprocess.TimeoutExpired:
            out = ''
        dt = time.time() - t0
        open(os.path.join(a.outdir, 'out', n), 'w').write(out)
        ok = 'THEOREM PROVED' in out
        return n, ok, dt, rc, len(hs), len(lem), proof_eqs(out) if ok else []

    with ThreadPoolExecutor(a.j) as ex, open(os.path.join(a.outdir, 'results.tsv'), 'a') as R, \
            open(os.path.join(a.outdir, 'solved.tsv'), 'a') as S:
        futs = [ex.submit(run, n) for n in todo]
        nok = 0
        for f in as_completed(futs):
            n, ok, dt, rc, nh, nl, eqs = f.result()
            R.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{rc}\t{nh}\t{nl}\n'); R.flush()
            if ok:
                nok += 1
                hl = [h for h in (twee_hint(e) for e in eqs) if h]
                open(os.path.join(a.outdir, 'hints', n), 'w').write(''.join(h + '\n' for h in hl))
                S.write(f'{n}\t1\t{dt:.2f}\n'); S.flush()   # (round 1: merge.py takes rows of round >= 1)
                print(f'PROVED {n} {dt:.1f}s hints={nh} lemmas={nl} steps={len(hl)}', flush=True)
        print(f'{nok}/{len(todo)} proved', flush=True)


if __name__ == '__main__':
    main()
