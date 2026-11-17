#!/usr/bin/env python3
"""exp4/genmoves.py GOALS OUT.tsv [-j J] [--secs S]: generalisations of the goal (Korovin's generalisation
abstraction, applied to the goal; Polya's inventor's paradox).

For each non-variable proper subterm u of the goal (either side), every occurrence of u is replaced by a fresh
variable. The result implies the goal (instantiate the variable by u), so if it is true it is a stronger lemma that
gives the goal at once, and it may be easier to prove (fewer symbols). Mace4 screens it in the real theory
(sizes 2..12, S seconds, default 10): 'ok' if no countermodel, else 'refuted'.
OUT.tsv in moves.py's format (goal, id, kind 'gen', the generalised goal, screen, detail), so sketch.py runs the
'ok' ones (as goals, like the weaker goals). Ids start at 1000 so they do not collide with moves.py's."""
import argparse, concurrent.futures as cf, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moves import ladr, mace, moves, signature
_tok = re.compile(r"[A-Za-z0-9_]+|[(),=]")
def parse(toks, i):
    t = toks[i]; i += 1
    if i < len(toks) and toks[i] == '(':
        i += 1; args = []
        while True:
            x, i = parse(toks, i); args.append(x)
            if toks[i] == ',': i += 1
            else: return (t, tuple(args)), i + 1
    return (t, ()), i
def show(t): return t[0] if not t[1] else f'{t[0]}({",".join(show(a) for a in t[1])})'
def isvar(t): return not t[1] and re.match(r'X\d+$', t[0])
def subterms(t):
    yield t
    for x in t[1]: yield from subterms(x)
def repl(t, u, v): return v if t == u else (t[0], tuple(repl(x, u, v) for x in t[1]))
def one(g):
    A, G = ladr(g); _, body = moves(signature(A + [G]), G)
    body = body.strip().rstrip('.').strip()
    while body.startswith('(') and body.endswith(')'): body = body[1:-1].strip()
    toks = _tok.findall(body); l, i = parse(toks, 0); assert toks[i] == '='; r, _ = parse(toks, i + 1)
    n = 1 + max([int(x[1:]) for x in re.findall(r'\bX\d+\b', body)] + [-1]); v = (f'X{n}', ())
    cands = []
    for u in list(subterms(l)) + list(subterms(r)):
        if isvar(u) or u in (l, r) or not u[1] and u[0] == 'e': continue
        c = f'{show(repl(l, u, v))} = {show(repl(r, u, v))}'
        if c not in cands: cands.append(c)
    rows = []
    for k, c in enumerate(cands):
        m = mace(A, c, a.secs, end=12)
        rows.append([g, 1000 + k, 'gen', c, 'refuted' if m else 'ok', f'countermodel {m}' if m else 'none up to 12'])
    return rows
ap = argparse.ArgumentParser(); ap.add_argument('goals'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=1); ap.add_argument('--secs', type=int, default=10)
a = ap.parse_args()
goals = [l.strip() for l in open(a.goals) if l.strip()]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for rows in ex.map(one, goals):
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
        f.flush()
