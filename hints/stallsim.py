#!/usr/bin/env python3
"""stallsim.py DIR[,DIR2..] [DIR0] [--rate 2000]: replay Veroff's stall criterion on
long twee runs.

DIR/out/<name> holds the output of a run with hints (twee-e16 or later:
WORK and HINTLOG lines, deterministic with --abstract-time). A stall limit
G only stops a run early and does not change the search before that, so for
each G the outcome of the stall-limited run follows from the full run:

  stop point = the first time G critical pairs pass without a new hint match
  solved     = the full run proved the goal before the stop point
  cost       = critical pairs until the proof, the stop point or the end

DIR0 (optional) is the same set without hints, for comparison. Rates turn
critical pairs into abstract seconds (default 2000 per second).
"""
import argparse, os, re

def parse(path):
    txt = open(path, errors='replace').read()
    m = re.search(r'^WORK considered=(\d+)', txt, re.M)
    work = int(m.group(1)) if m else None
    log = []
    m = re.search(r'^HINTLOG(.*)$', txt, re.M)
    if m:
        log = [int(x.split(':')[0]) for x in m.group(1).split()]
    return 'RESULT: Theorem' in txt, work, log

def parse_p9(path):
    """Prover9 output: work = given clauses, log = givens selected as hint matchers (H)."""
    log, work = [], 0
    for line in open(path, errors='replace'):
        if line.startswith('given #'):
            k = int(line[7:line.index(' ', 7)])
            work = k
            if '(H,' in line:
                log.append(k)
    txt_ok = 'THEOREM PROVED' in open(path, errors='replace').read()
    return txt_ok, work, log

def stall_point(log, G, end):
    """First critical-pair count at which G pass without a new match."""
    last = 0
    for c in log:
        if c - last > G:
            return last + G
        last = c
    return last + G if end - last > G else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('dir0', nargs='?')
    ap.add_argument('--rate', type=int, default=2000)
    ap.add_argument('--gaps', default='5,10,20,30,60,120')
    ap.add_argument('--p9', action='store_true', help='Prover9 outputs; work and gaps in given clauses (use --rate 1)')
    ap.add_argument('--limits', help='also replay per-problem time limits (abstract s, comma-separated)')
    ap.add_argument('--on-hints', type=float, help='only print the unsolved runs still on hints at the end for this gap (s): the ones to extend')
    a = ap.parse_args()
    global parse
    if a.p9:
        parse = parse_p9
    # DIR may be D1,D2,...: a run in a later dir (e.g. the same problem rerun
    # with a longer budget; abstract time replays the first part exactly)
    # replaces the earlier one
    def load(dirs):
        runs = {}
        for d in dirs.split(','):
            for n in sorted(os.listdir(os.path.join(d, 'out'))):
                if not n.endswith('.tmp'):
                    r = parse(os.path.join(d, 'out', n))
                    if r[1] is not None:
                        runs[n] = r
        return runs
    runs = load(a.dir)
    R = a.rate
    if a.on_hints is not None:
        for n, (ok, work, log) in runs.items():
            if not ok and stall_point(log, int(a.on_hints * R), work) is None:
                print(n)
        return
    nsol = sum(r[0] for r in runs.values()); tot = sum(r[1] for r in runs.values())
    print(f'{a.dir}: {len(runs)} runs, solved {nsol}, work {tot / R / 3600:.2f} abstract h')
    if a.dir0:
        r0 = {n: r for n, r in load(a.dir0).items() if n in runs}
        s0 = sum(r[0] for r in r0.values() if r[1] is not None)
        w0 = sum(r[1] for r in r0.values())
        both = sum(1 for n in r0 if r0[n][0] and runs[n][0])
        print(f'{a.dir0} (no hints): solved {s0}, work {w0 / R / 3600:.2f} abstract h; both {both}, '
              f'hints only {nsol - both}, no-hints only {s0 - both}')
    print('gap(s)  solved  work(h)  on-hints-at-end(unsolved)')
    for g in a.gaps.split(','):
        G = int(float(g) * R)
        s = cost = on = 0
        for n, (ok, work, log) in runs.items():
            sp = stall_point(log, G, work)
            if ok and (sp is None or work <= sp):
                s += 1; cost += work
            else:
                cost += work if sp is None else min(sp, work)
                if not ok and sp is None:
                    on += 1
        print(f'{g:>6}  {s:>6}  {cost / R / 3600:7.2f}  {on}')
    if a.limits:
        print('limit(s)  solved  work(h)')
        for t in a.limits.split(','):
            T = float(t) * R
            s = sum(1 for ok, work, _ in runs.values() if ok and work <= T)
            cost = sum(min(work, T) for _, work, _ in runs.values())
            print(f'{t:>8}  {s:>6}  {cost / R / 3600:7.2f}')
    # when did solved and unsolved runs make their last new match?
    def last(log): return log[-1] / R if log else 0
    sl = sorted(last(r[2]) for r in runs.values() if r[0])
    ul = sorted(last(r[2]) for r in runs.values() if not r[0])
    q = lambda xs: [round(xs[int(f * (len(xs) - 1))], 1) for f in (0.25, 0.5, 0.75, 1.0)] if xs else []
    print('last new match (abstract s), quartiles and max: solved', q(sl), 'unsolved', q(ul))
    pr = sorted(r[1] / R for r in runs.values() if r[0])
    print('proof found at (abstract s), quartiles and max:', q(pr))

if __name__ == '__main__':
    main()
