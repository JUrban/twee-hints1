#!/usr/bin/env python3
"""Lemma import: add the statements of proven sibling goals as axioms.

All goals X__goal_N of one original X have the same axioms, so a sibling
goal proven from them is a theorem of the theory and a sound extra axiom.
(As in CASC LTB, where conjectures proven earlier in a batch may be used.)

lemmas.py NAMES SOLVED OUTDIR [-m M] [--after]
  NAMES   problems to write
  SOLVED  file whose first column lists proven problems
  OUTDIR  gets OUTDIR/<name>.p: the problem plus up to M lemmas, the
          proven siblings with the nearest goal numbers below N (with
          --after also above N). Only unit equations are used.
"""
import argparse, collections, os, re

PROB = '/project/AIM60k/problems/tptp'

def split(name):
    o, n = name.rsplit('__goal_', 1)
    return o, int(n)

def conjecture(name):
    txt = open(os.path.join(PROB, name + '.p')).read()
    m = re.search(r'fof\(\w+,\s*conjecture,\s*(.*)\)\.\s*$', txt, re.S)
    return m.group(1).strip() if m else None

def unit_eq(f):
    body = re.sub(r'!\s*\[[^\]]*\]\s*:\s*', '', f)
    return not any(c in body for c in ('|', '~', '=>', '&', '!=')) and body.count('=') == 1

def by_original(names):
    solved = collections.defaultdict(set)
    for n in names:
        o, k = split(n)
        solved[o].add(k)
    return solved

def lemma_problem(name, solved, m, after=False):
    """Text of problem NAME with up to M proven siblings (solved: original ->
    set of goal numbers) as extra axioms, and the number of lemmas added."""
    o, k = split(name)
    cands = sorted((j for j in solved.get(o, ()) if j != k and (after or j < k)), key=lambda j: (abs(k - j), j))
    lem = []
    for j in cands:
        if len(lem) >= m:
            break
        f = conjecture(f'{o}__goal_{j}')
        if f and unit_eq(f):
            lem.append((j, f))
    txt = open(os.path.join(PROB, name + '.p')).read().rstrip('\n') + '\n'
    for j, f in lem:
        txt += f'fof(lemma_goal_{j},axiom,{f}).\n'
    return txt, len(lem)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('solved'); ap.add_argument('outdir')
    ap.add_argument('-m', type=int, default=10)
    ap.add_argument('--after', action='store_true')
    a = ap.parse_args()
    solved = by_original(line.split()[0] for line in open(a.solved) if line.strip())
    os.makedirs(a.outdir, exist_ok=True)
    tot = 0
    for line in open(a.names):
        name = line.split()[0]
        txt, n = lemma_problem(name, solved, a.m, a.after)
        with open(os.path.join(a.outdir, name + '.p'), 'w') as out:
            out.write(txt)
        tot += n
    print('lemmas', tot)

if __name__ == '__main__':
    main()
