#!/usr/bin/env python3
"""Veroff-style sketches: hints from proofs under extra assumptions.

For each goal X__goal_N, assume the statements of its M nearest sibling
goals below N as axioms, proven or not (an easier, possibly unsound
problem), and run twee on it. When that finds a proof, its steps and the
assumed statements are written as hints for the real problem; hints only
guide the search, so this is sound.

sketch.py NAMES OUTDIR [-m M] [--timeout S] [-j N] [--twee BIN] [--args ...]
          [--per FLAG:DIR]
Writes OUTDIR/hints/<name> and OUTDIR/results.tsv.
"""
import argparse, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, lemmas

def canon_key(l, r, sig):
    return min(hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig))

ALL = '/project/AIM60k/problems/00ALL'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('outdir')
    ap.add_argument('-m', type=int, default=3)
    ap.add_argument('--timeout', type=float, default=5)
    ap.add_argument('-j', type=int, default=3)
    ap.add_argument('--twee', default='/project/bin/twee')
    ap.add_argument('--args', default='')
    ap.add_argument('--per', action='append', default=[])
    a = ap.parse_args()
    allgoals = lemmas.by_original(l.split()[0] for l in open(ALL) if l.strip())
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    for d in ('probs', 'hints'):
        os.makedirs(os.path.join(a.outdir, d), exist_ok=True)
    sigs = {}

    def one(name):
        txt, n = lemmas.lemma_problem(name, allgoals, a.m)
        path = os.path.join(a.outdir, 'probs', name + '.p')
        with open(path, 'w') as f:
            f.write(txt)
        cmd = [a.twee, path, '--max-time', str(a.timeout), '--no-colour', '--quiet', '--no-proof',
               '--print-hints'] + a.args.split()
        for spec in a.per:
            flag, d = spec.split(':', 1)
            p = os.path.join(d, name)
            if os.path.exists(p):
                cmd += ['--' + flag, p]
        t0 = time.time()
        try:
            out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=a.timeout + 30).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired:
            out = ''
        dt = time.time() - t0
        if 'HINTS-END' not in out:
            return name, False, dt, 0
        o = name.rsplit('__goal_', 1)[0]
        if o not in sigs:
            sigs[o] = hintlib.problem_signature(name)
        sig = sigs[o]
        L, G = hintlib.extract_hints(out)
        assumed = [hintlib._split_eq(f) for f in
                   [line.split('axiom,', 1)[1].rsplit(').', 1)[0] for line in txt.splitlines() if line.startswith('fof(lemma_goal_')]]
        seen, hs = set(), []
        for l, r in [x for x in assumed if x] + L + G:
            if l == r:
                continue
            k = canon_key(l, r, sig)
            if k[0] != k[1] and k not in seen:
                seen.add(k); hs.append(k)
        with open(os.path.join(a.outdir, 'hints', name), 'w') as f:
            for l, r in hs:
                f.write(f'{l}\t{r}\n')
        return name, True, dt, len(hs)

    t0 = time.time(); ok = 0
    with ThreadPoolExecutor(a.j) as ex, open(os.path.join(a.outdir, 'results.tsv'), 'w') as rf:
        for k, f in enumerate(as_completed([ex.submit(one, n) for n in names])):
            n, s, dt, nh = f.result()
            ok += s
            rf.write(f'{n}\t{"THM" if s else "NO"}\t{dt:.2f}\t{nh}\n'); rf.flush()
    print(f'done {len(names)} sketched={ok} {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
