#!/usr/bin/env python3
"""Collect ENIGMA-style training data: every rule twee added, labelled by
whether it is a lemma of the proof found.

given.py NAMES OUTDIR [--twee BIN] [--timeout T] [-j N] [--args ...] [--hints-dir D]
writes OUTDIR/<name>: one line per added rule, `label<TAB>index<TAB>lhs<TAB>rhs`,
label 1 = proof lemma or goal, 0 = other rule, -1 = axiom; generalised
(skolems -> variables). Problems that are not solved get no file.
"""
import argparse, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib

def key(l, r, sig):
    a = hintlib.generalize(l, r, sig)
    b = hintlib.generalize(r, l, sig)
    return min(a, (b[1], b[0]))

def axioms(name):
    txt = open(os.path.join(hintlib.PROB, name + '.p')).read()
    out = []
    for m in re.finditer(r'(?:fof|cnf)\(\s*[^,]*,\s*axiom\s*,(.*?)\)\.\s*$', txt, re.S | re.M):
        e = hintlib._split_eq(m.group(1))
        if e:
            out.append(e)
    return out

def parse_given_parents(text):
    """[(lhs, rhs, parent1, parent2)] from --print-given output; parents are
    rule numbers (the rule logged at position k has number k+1), 0 = none."""
    i = text.find('GIVEN-BEGIN'); j = text.find('GIVEN-END')
    if i < 0 or j < 0:
        return []
    block = text[i + 11:j]
    out = []
    if '% parents' not in block:
        return [(l, r, 0, 0) for m in hintlib._hintre.finditer(block + 'HINTS-')
                for e in [hintlib._split_eq(m.group(1))] if e for l, r in [e]]
    for chunk in block.split('% parents ')[1:]:
        head, _, rest = chunk.partition('\n')
        p1, p2 = (int(x) for x in head.split()[:2])
        a = rest.find('(hint, axiom,'); b = rest.rfind(').')
        if a < 0 or b < 0:
            continue
        e = hintlib._split_eq(rest[a + 13:b])
        if e:
            out.append((e[0], e[1], p1, p2))
        else:
            out.append(None)
    return out

def parse_given(text):
    return [(x[0], x[1]) if x else ('', '') for x in parse_given_parents(text)]

def run(name, a):
    cmd = [a.twee, os.path.join(hintlib.PROB, name + '.p'), '--quiet', '--no-proof',
           '--print-hints', '--print-given'] + a.args.split()
    if a.hints_dir:
        hf = os.path.join(a.hints_dir, name)
        if os.path.exists(hf):
            cmd += ['--hints-file', hf]
    for spec in a.per:
        flag, d = spec.split(':', 1)
        p = os.path.join(d, name)
        if os.path.exists(p):
            cmd += ['--' + flag, p]
    try:
        out = subprocess.run(['timeout', str(a.timeout)] + cmd, capture_output=True,
                             text=True).stdout
    except Exception:
        return name, None
    if 'RESULT: Theorem' not in out:
        return name, None
    sig = hintlib.problem_signature(name)
    lemmas, goals = hintlib.extract_hints(out)
    pos = set(key(l, r, sig) for l, r in lemmas + goals)
    ax = set(key(l, r, sig) for l, r in axioms(name))
    rows = []
    for idx, x in enumerate(parse_given_parents(out)):
        if x is None or x[0] == x[1]:
            continue
        l, r, p1, p2 = x
        k = key(l, r, sig)
        lab = -1 if k in ax else (1 if k in pos else 0)
        rows.append(f'{lab}\t{idx}\t{k[0]}\t{k[1]}\t{p1}\t{p2}\n')
    return name, rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('outdir')
    ap.add_argument('--twee', default='/project/bin/twee-h9')
    ap.add_argument('--timeout', type=float, default=4)
    ap.add_argument('-j', type=int, default=10)
    ap.add_argument('--args', default='')
    ap.add_argument('--hints-dir')
    ap.add_argument('--per', action='append', default=[], help='FLAG:DIR adds --FLAG DIR/<name>')
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    n = ok = 0
    with ThreadPoolExecutor(a.j) as ex:
        for name, rows in ex.map(lambda x: run(x, a), names):
            n += 1
            if rows:
                ok += 1
                open(os.path.join(a.outdir, name), 'w').writelines(rows)
            if n % 200 == 0:
                print(f'{n}/{len(names)} solved={ok}', flush=True)
    print(f'done {n} solved={ok}')

if __name__ == '__main__':
    main()
