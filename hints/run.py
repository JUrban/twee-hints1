#!/usr/bin/env python3
"""Run twee on many AIM60k problems in parallel.

usage: run.py NAMES_FILE OUTDIR [--twee BIN] [--timeout S] [-j N]
              [--hints-dir DIR] [--args "..."]

Writes OUTDIR/results.tsv (name, status, seconds) and OUTDIR/out/<name>.out
(the full twee output, only for solved problems unless --keep-all).
With --hints-dir, passes DIR/<name> as --hints-file when it exists
(or a single global file with --hints-file).
"""
import argparse, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROB = '/project/AIM60k/problems/tptp'

def run_one(name, a):
    cmd = [a.twee, os.path.join(PROB, name + '.p'), '--max-time', str(a.timeout),
           '--no-colour'] + a.args.split()
    hf = None
    if a.hints_file:
        hf = a.hints_file
    elif a.hints_dir:
        p = os.path.join(a.hints_dir, name)
        if os.path.exists(p):
            hf = p
    if hf:
        cmd += ['--hints-file', hf]
    for spec in a.per:
        flag, d = spec.split(':', 1)
        p = os.path.join(d, name)
        if os.path.exists(p):
            cmd += ['--' + flag, p]
    if a.rts:
        cmd += ['+RTS'] + a.rts.split() + ['-RTS']
    t0 = time.time()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=a.timeout + 10)
        out = p.stdout.decode('utf8', 'replace')
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b'').decode('utf8', 'replace') + '\nKILLED\n'
    dt = time.time() - t0
    if 'RESULT: Theorem' in out or 'SZS status Theorem' in out or 'SZS status Unsatisfiable' in out:
        st = 'THM'
    elif 'RESULT: GaveUp' in out or 'GaveUp' in out:
        st = 'GU'
    elif 'Timeout' in out or 'KILLED' in out:
        st = 'TO'
    else:
        st = 'ERR'
    if st == 'THM' or a.keep_all:
        with open(os.path.join(a.outdir, 'out', name + '.out'), 'w') as f:
            f.write(out)
    return name, st, dt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names')
    ap.add_argument('outdir')
    ap.add_argument('--twee', default='/project/bin/twee')
    ap.add_argument('--timeout', type=float, default=2)
    ap.add_argument('-j', type=int, default=20)
    ap.add_argument('--args', default='')
    ap.add_argument('--rts', default='')
    ap.add_argument('--hints-dir')
    ap.add_argument('--hints-file')
    ap.add_argument('--keep-all', action='store_true')
    ap.add_argument('--per', action='append', default=[],
                    help='FLAG:DIR adds --FLAG DIR/<name> when that file exists')
    a = ap.parse_args()
    names = [l.strip() for l in open(a.names) if l.strip()]
    os.makedirs(os.path.join(a.outdir, 'out'), exist_ok=True)
    res = os.path.join(a.outdir, 'results.tsv')
    done = set()
    if os.path.exists(res):
        done = {l.split('\t')[0] for l in open(res)}
    todo = [n for n in names if n not in done]
    t0 = time.time(); k = 0; nthm = 0
    with open(res, 'a') as rf, ThreadPoolExecutor(a.j) as ex:
        futs = [ex.submit(run_one, n, a) for n in todo]
        for f in as_completed(futs):
            n, st, dt = f.result()
            rf.write(f'{n}\t{st}\t{dt:.2f}\n'); rf.flush()
            k += 1; nthm += st == 'THM'
            if k % 200 == 0:
                print(f'{k}/{len(todo)} thm={nthm} {time.time()-t0:.0f}s', file=sys.stderr, flush=True)
    print(f'done {k} thm={nthm} {time.time()-t0:.0f}s', file=sys.stderr)

if __name__ == '__main__':
    main()
