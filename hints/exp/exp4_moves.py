#!/usr/bin/env python3
"""exp4/moves.py GOAL [--secs S] [--out TSV]: up moves and weaker goals for one AIM goal, screened with Mace4.

Moves (notes/2026-11-17-lattice-construction.md):
  group    f(X..) = g(X..) for two function symbols of the same arity (Korovin's signature grouping)
  filter   f(..X..) = f(..Y..): f ignores one argument (Korovin's argument filtering)
  law      a law of loop theory over the theory's symbols (commutativity, associativity, flexibility, the
           alternative, inverse, Moufang and Bol laws, an inner map trivial)
  inst     a weaker goal: two goal variables identified, or one set to e (grouping of Skolem constants)
Mace4 (/project/bin/mace4, sizes 2..N, S seconds each):
  for an up move S: 'collapse' if T+S has no model of size 2..N (none found; a heuristic), 'group' if it has no
  non-associative model of size 2..12 (S probably forces a group, where AIM goals are trivial), else 'ok';
  for a weaker goal: always 'ok' (an instance of a true goal is true).
Writes TSV rows: goal, move id, kind, the move (LADR syntax, = TPTP term syntax), screen, detail."""
import argparse, itertools, os, re, subprocess, tempfile
PROB = '/project/AIM60k/problems/tptp'
T2L = '/project/Prover9-new/bin/tptp_to_ladr'
MACE = '/project/bin/mace4'
V = 'ABCDEFGH'

def ladr(goal):
    """(assumption lines, goal formula) of the problem in LADR syntax"""
    txt = subprocess.run([T2L], stdin=open(f'{PROB}/{goal}.p'), capture_output=True, text=True).stdout
    a = txt[txt.index('formulas(assumptions).') + 22: txt.index('end_of_list.')]
    g = txt[txt.index('formulas(goals).') + 16:]
    g = g[:g.index('end_of_list.')]
    strip = lambda s: re.sub(r'\s*#\s*label\([^)]*\)', '', s).strip()
    return [strip(x) for x in a.strip().splitlines() if x.strip()], strip(g.strip())

def signature(lines):
    sig = {}
    for l in lines:
        for m in re.finditer(r'\b([a-z]\w*)\(', l):
            f = m.group(1); i = m.end(); depth, n = 1, 1
            while depth:
                c = l[i]
                if c == '(': depth += 1
                elif c == ')': depth -= 1
                elif c == ',' and depth == 1: n += 1
                i += 1
            sig[f] = n
    return sig

def app(f, args): return f'{f}({",".join(args)})'

def moves(sig, goal):
    out = []
    fs = sorted(sig)
    for f, g in itertools.combinations(fs, 2):
        if sig[f] == sig[g]:
            xs = list(V[:sig[f]]); out.append(('group', f'{app(f, xs)} = {app(g, xs)}'))
    for f in fs:
        n = sig[f]
        for i in range(n):
            xs = list(V[:n]); ys = list(xs); ys[i] = V[n]
            out.append(('filter', f'{app(f, xs)} = {app(f, ys)}'))
    m = lambda x, y: f'm({x},{y})'
    laws = [m('A', 'B') + ' = ' + m('B', 'A'),
            m(m('A', 'B'), 'C') + ' = ' + m('A', m('B', 'C')),
            m(m('A', 'B'), 'A') + ' = ' + m('A', m('B', 'A')),
            m('A', m('A', 'B')) + ' = ' + m(m('A', 'A'), 'B'),
            m(m('A', 'B'), 'B') + ' = ' + m('A', m('B', 'B')),
            m('ld(A,e)', m('A', 'B')) + ' = B',
            m(m('B', 'A'), 'rd(e,A)') + ' = B',
            m(m('A', m('B', 'A')), 'C') + ' = ' + m('A', m('B', m('A', 'C'))),
            m(m(m('C', 'A'), 'B'), 'A') + ' = ' + m('C', m(m('A', 'B'), 'A')),
            m(m('A', 'B'), m('C', 'A')) + ' = ' + m(m('A', m('B', 'C')), 'A')]
    if 'm' in sig and 'ld' in sig and 'rd' in sig:
        out += [('law', x) for x in laws]
    for f, triv in (('t', 'A'), ('l', 'A'), ('r', 'A'), ('k', 'e'), ('a', 'e')):
        if f in sig: out.append(('law', f'{app(f, list(V[:sig[f]]))} = {triv}'))
    # weaker goals: instances of the goal
    q = re.match(r'\(?\s*((?:all \w+\s+)*)(.*?)\)?$', goal)
    vs = re.findall(r'all (\w+)', goal); body = goal
    body = re.sub(r'all \w+\s+', '', body).strip()
    while body.startswith('(') and body.endswith(')'): body = body[1:-1].strip()
    sub = lambda b, x, y: re.sub(rf'\b{x}\b', y, b)
    for x, y in itertools.combinations(vs, 2):
        out.append(('inst', sub(body, y, x)))
    for x in vs:
        out.append(('inst', sub(body, x, 'e')))
    return out, body

def mace(assumptions, goal, secs, end=8):
    with tempfile.NamedTemporaryFile('w', suffix='.in', delete=False) as f:
        f.write('set(prolog_style_variables).\nformulas(assumptions).\n' + ''.join(a + '\n' for a in assumptions)
                + 'end_of_list.\n')
        if goal: f.write(f'formulas(goals).\n{goal}.\nend_of_list.\n')
        f.write(f'assign(max_seconds, {secs}).\nassign(start_size, 2).\nassign(end_size, {end}).\n')
        p = f.name
    try:
        o = subprocess.run([MACE, '-f', p], capture_output=True, text=True, timeout=secs + 10).stdout
    except subprocess.TimeoutExpired:
        o = ''
    os.unlink(p)
    m = re.search(r'interpretation\( (\d+)', o)
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('goal'); ap.add_argument('--secs', type=int, default=5)
    ap.add_argument('--out'); a = ap.parse_args()
    A, G = ladr(a.goal); sig = signature(A + [G]); mv, body = moves(sig, G)
    rows = []
    for i, (kind, eq) in enumerate(mv):
        if kind == 'inst':
            rows.append((kind, eq, 'ok', '')); continue
        n = mace(A + [eq + '.'], None, a.secs)
        if n is None: rows.append((kind, eq, 'collapse', 'no model 2..8')); continue
        # the goal is true in T, so it is true in T+S: a countermodel to it cannot exist. Instead: does T+S still
        # have a non-associative model? If not, S (probably) forces a group, where these goals become trivial.
        c = mace(A + [eq + '.'], 'm(m(A,B),C) = m(A,m(B,C))', a.secs, end=12)   # 12: the smallest non-associative Moufang loop
        rows.append((kind, eq, 'ok' if c else 'group', f'model {n}' + (f', nonassociative {c}' if c else ', no nonassociative 2..12')))
    f = open(a.out, 'a') if a.out else None
    for i, (kind, eq, scr, det) in enumerate(rows):
        line = f'{a.goal}\t{i}\t{kind}\t{eq}\t{scr}\t{det}'
        print(line) if not f else f.write(line + '\n')

if __name__ == '__main__':
    main()
