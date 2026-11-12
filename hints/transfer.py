#!/usr/bin/env python3
"""Hint-transfer benchmark: run problems with hints taken from the proofs
of OTHER solved problems (leave-one-out), with a hint-selection strategy.

usage: transfer.py NAMES HINTDIR OUTDIR [--strategy all|near:K|before:K|none]
                   [--timeout S] [-j N] [--twee BIN] [--args "..."]
"""
import argparse, collections, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROB = '/project/AIM60k/problems/tptp'
LINES = '/project/hintwork/sets/lines.tsv'

def load_lines():
    d = {}
    for l in open(LINES):
        n, x = l.split('\t'); d[n] = int(x)
    return d

def orig_of(n):
    return n.split('__goal_')[0]

_knn = None

def select(name, strategy, solved_by_orig, lines, hintdir):
    global _knn
    if strategy == 'none':
        return []
    if strategy.startswith('knn'):
        if _knn is None:
            import hintsel as sel
            _knn = sel.KNN(hintdir)
        _, k, n = strategy.split(':')
        return _knn.select(name, int(k), int(n), same_orig=strategy.startswith('knno'))
    cands = [m for m in solved_by_orig.get(orig_of(name), []) if m != name]
    L = lines[name]
    if strategy.startswith('near:'):
        k = int(strategy.split(':')[1])
        cands = sorted(cands, key=lambda m: abs(lines[m] - L))[:k]
    elif strategy.startswith('before:'):
        k = int(strategy.split(':')[1])
        cands = sorted([m for m in cands if lines[m] < L], key=lambda m: L - lines[m])[:k]
    cnt = collections.Counter()
    for m in cands:
        for l in open(os.path.join(hintdir, m)):
            if '\t' in l:
                cnt[l.rstrip('\n')] += 1
    return [h for h, _ in cnt.most_common()]

def run_one(name, hints, a):
    cmd = [a.twee, os.path.join(PROB, name + '.p'), '--max-time', str(a.timeout),
           '--no-colour', '--quiet', '--no-proof'] + a.args.split()
    hp = None
    if hints:
        hp = os.path.join(a.outdir, 'tmp', name + '.hints')
        with open(hp, 'w') as f:
            f.write('\n'.join(hints) + '\n')
        cmd += ['--hints-file', hp]
    t0 = time.time()
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=a.timeout + 30).stdout.decode('utf8', 'replace')
    except subprocess.TimeoutExpired:
        out = 'KILLED'
    dt = time.time() - t0
    if hp:
        os.unlink(hp)
    ok = 'RESULT: Theorem' in out
    stats = next((l for l in out.splitlines() if l.startswith('HINTSTATS')), '')
    return name, ok, dt, len(hints), stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('hintdir'); ap.add_argument('outdir')
    ap.add_argument('--strategy', default='all')
    ap.add_argument('--timeout', type=float, default=4)
    ap.add_argument('-j', type=int, default=20)
    ap.add_argument('--twee', default='/project/bin/twee')
    ap.add_argument('--args', default='')
    a = ap.parse_args()
    names = [l.strip() for l in open(a.names) if l.strip()]
    lines = load_lines()
    solved_by_orig = collections.defaultdict(list)
    for m in os.listdir(a.hintdir):
        solved_by_orig[orig_of(m)].append(m)
    os.makedirs(os.path.join(a.outdir, 'tmp'), exist_ok=True)
    t0 = time.time()
    res = []
    with ThreadPoolExecutor(a.j) as ex:
        futs = [ex.submit(run_one, n, select(n, a.strategy, solved_by_orig, lines, a.hintdir), a)
                for n in names]
        for f in as_completed(futs):
            res.append(f.result())
    with open(os.path.join(a.outdir, 'results.tsv'), 'w') as f:
        for n, ok, dt, nh, st in sorted(res):
            f.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{nh}\t{st}\n')
    solved = sum(r[1] for r in res)
    par2 = sum(r[2] if r[1] else 2 * a.timeout for r in res) / len(res)
    msg = f'{a.outdir}: solved {solved}/{len(res)} par2 {par2:.2f} wall {time.time()-t0:.0f}s'
    print(msg)
    with open(os.path.join(os.path.dirname(a.outdir.rstrip('/')), 'summary.txt'), 'a') as f:
        f.write(msg + f'  [{a.strategy} {a.args}]\n')

if __name__ == '__main__':
    main()
