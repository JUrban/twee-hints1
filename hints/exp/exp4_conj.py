#!/usr/bin/env python3
"""exp4/conj.py GOALS OUT.tsv [-j J] [--nf NF.tsv]: a model-based conjecturer for intermediate lemmas (QuickSpec's
idea, whose prover is twee; and how Kinyon and Veroff found AIM lemmas, from finite models).

1. Models of the goal's theory T (the problem's assumptions, LADR via tptp_to_ladr), collected with Mace4:
   non-associative ones (T + m(m(c1,c2),c3) != m(c1,m(c2,c3))), up to 25 per size from 2 to 12, 15 s per size;
   and any ones (groups among them), up to 10 per size from 2 to 8, 5 s per size.
2. Candidate terms: the subterms of the goal's two sides and of its normal forms (nf.py's twee-e56 outputs,
   GOALNF lines in NF.tsv.d/<goal>; their constants x<i> are the goal's variables X<i>), plus the goal's
   variables and e.
3. Conjectures: every equation s = t between two candidate terms, not both from the same side's term tree only
   (at least one of them from the goal or its normal forms on each side, or one is a variable or e), that holds
   in every collected model (numpy evaluation over all assignments of its variables), and is not the goal or a
   pair of its normal forms itself.
OUT.tsv: goal, conjecture id, conjecture (LADR syntax), kind (LR: a left subterm = a right subterm; LL/RR: within
one side; LV/RV: a subterm = a variable or e), models it was checked in. Ids start at 3000."""
import argparse, concurrent.futures as cf, itertools, os, re, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moves import ladr, moves, signature
MACE = '/project/bin/mace4'
_tok = re.compile(r"[A-Za-z0-9_]+|[(),=]")
def parse(toks, i=0):
    t = toks[i]; i += 1
    if i < len(toks) and toks[i] == '(':
        i += 1; args = []
        while True:
            x, i = parse(toks, i); args.append(x)
            if toks[i] == ',': i += 1
            else: return (t, tuple(args)), i + 1
    return (t, ()), i
def show(t): return t[0] if not t[1] else f'{t[0]}({",".join(show(a) for a in t[1])})'
def subterms(t):
    yield t
    for x in t[1]: yield from subterms(x)
def isvar(t): return not t[1] and re.match(r'X\d+$', t[0]) is not None
def tvars(t): return {s[0] for s in subterms(t) if isvar(s)}

def mace_models(A, extra, start, end, n, secs):
    with tempfile.NamedTemporaryFile('w', suffix='.in', delete=False) as f:
        f.write('set(prolog_style_variables).\nformulas(assumptions).\n' + ''.join(x + '\n' for x in A + extra)
                + f'end_of_list.\nassign(max_seconds, {secs}).\nassign(start_size, {start}).\n'
                + f'assign(end_size, {end}).\nassign(max_models, {n}).\n')
        p = f.name
    try: o = subprocess.run([MACE, '-f', p], capture_output=True, text=True, timeout=secs + 10).stdout
    except subprocess.TimeoutExpired as e: o = (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
    os.unlink(p)
    models = []
    for block in o.split('interpretation(')[1:]:
        size = int(block.split(',')[0])
        fs = {}
        for m in re.finditer(r'function\((\w+)(\([_,]*\))?, \[([\d,\s]*)\]\)', block):
            ar = m.group(2).count('_') if m.group(2) else 0
            fs[m.group(1)] = (ar, np.array([int(x) for x in m.group(3).replace('\n', ' ').split(',')]))
        models.append((size, fs))
    return models

def models_of(A):
    ms = []
    for size in range(2, 13):
        ms += mace_models(A, ['m(m(c1,c2),c3) != m(c1,m(c2,c3)).'], size, size, 25, 15)
    for size in range(2, 9):
        ms += mace_models(A, [], size, size, 10, 5)
    return ms

def evaluate(t, size, fs, env):
    if isvar(t): return env[t[0]]
    ar, tab = fs[t[0]]
    if ar == 0: return tab[0]
    idx = 0
    for a in t[1]: idx = idx * size + evaluate(a, size, fs, env)
    return tab[idx]

def holds(s, t, models):
    vs = sorted(tvars(s) | tvars(t))
    for size, fs in models:
        if any(x[0] not in fs for x in list(subterms(s)) + list(subterms(t)) if not isvar(x)): return False
        grids = np.meshgrid(*[np.arange(size)] * len(vs), indexing='ij') if vs else []
        env = {v: g for v, g in zip(vs, grids)}
        if not np.all(evaluate(s, size, fs, env) == evaluate(t, size, fs, env)): return False
    return True

def nf_terms(path):
    side = {'L': [], 'R': []}
    if not path or not os.path.exists(path): return side
    for l in open(path, errors='replace'):
        m = re.match(r'GOALNF ([LR]) fof\(nf, axiom, (.*)\)\.$', l.rstrip('\n'))
        if m:
            s = re.sub(r'\bx(\d+)\b', r'X\1', m.group(2).replace(' ', ''))
            side[m.group(1)].append(parse(_tok.findall(s[:len(s) // 2]))[0])
    return side

def one(g):
    A, G = ladr(g); _, body = moves(signature(A + [G]), G)
    body = body.strip().rstrip('.').strip()
    while body.startswith('(') and body.endswith(')'): body = body[1:-1].strip()
    toks = _tok.findall(body); L, i = parse(toks); R, _ = parse(toks, i + 1)
    nf = nf_terms(f'{a.nf}.d/{g}' if a.nf else None)
    Ls = {t for x in [L] + nf['L'] for t in subterms(x) if not isvar(t)}
    Rs = {t for x in [R] + nf['R'] for t in subterms(x) if not isvar(t)}
    atoms = sorted({('e', ())} | {(v, ()) for v in tvars(L) | tvars(R)})
    tops = {frozenset((x, y)) for x in [L] + nf['L'] for y in [R] + nf['R']}
    models = models_of(A)
    pairs = []
    for s in sorted(Ls):
        for t in sorted(Rs):
            if s != t: pairs.append((s, t, 'LR'))
    for side, S in (('L', Ls), ('R', Rs)):
        for s, t in itertools.combinations(sorted(S), 2): pairs.append((s, t, side * 2))
        for s in sorted(S):
            for t in atoms: pairs.append((s, t, side + 'V'))
    rows, seen = [], set()
    for s, t, kind in pairs:
        k = frozenset((s, t))
        if k in seen or k in tops or s == t: continue
        seen.add(k)
        if holds(s, t, models):
            rows.append([g, 3000 + len(rows), f'{show(s)} = {show(t)}', kind, len(models)])
    return rows, len(models), len(pairs)

ap = argparse.ArgumentParser(); ap.add_argument('goals'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=1); ap.add_argument('--nf')
a = ap.parse_args()
goals = [l.strip() for l in open(a.goals) if l.strip()]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for g, (rows, nm, npairs) in zip(goals, ex.map(one, goals)):
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
        print(g, 'models', nm, 'pairs', npairs, 'conjectures', len(rows), flush=True)
        f.flush()
