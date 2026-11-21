#!/usr/bin/env python3
"""(21 Nov 07:30) Load-free comparison of from-zero arms run at different times.

  abscurve.py SET REF DIR... [--at M,...]

setcurve.py compares arms by wall minutes, which is fair only for arms run side by side: the machine's speed per
abstract second changes with its load (failed 5 s L0 runs took 5.6-6.0 CPU s in exp44/45 at night, 4.7-5.0 s in
exp48). Here each run's CPU time (results.tsv dt) is turned into abstract seconds by its arm's CPU per abstract
second in the same 15-minute window (the median dt/5 of that window's failed plain 5 s L0 runs; cumulative to date
when the window has fewer than 30). A(t) = an arm's abstract worker seconds by wall time t. For each M in --at, at
REF's A(M minutes), every arm's wall time with the same A and its SET goals solved then (proof-file mtimes, as
setcurve.py).
"""
import bisect, os, sys

L = '/project/hintwork/loops'


def acurve(d):
    rows = [l.rstrip('\n').split('\t') for l in open(f'{L}/{d}/r1/results.tsv') if l.strip()]
    ev = []
    for w in rows:
        t = float(next(x for x in w if x.startswith('t='))[2:])
        plain = w[4] == 'L0' and w[1] == 'NO' and not ({'q=1', 'r=1', 'f=1'} & set(w[7:]))
        ev.append((t, float(w[2]), plain))
    ev.sort()
    win = {}
    for t, dt, p in ev:
        if p:
            win.setdefault(int(t // 900), []).append(dt)
    med = lambda v: sorted(v)[len(v) // 2]
    cum = []; ks = {}
    for b in range(0, int(ev[-1][0] // 900) + 1):
        v = win.get(b, []); cum += v
        # (the median: Z6's first window had 17 such runs, four of them 50-73 s)
        ks[b] = med(v) / 5 if len(v) >= 30 else (med(cum) / 5 if cum else 1.0)
    ts, As = [], []; a = 0.0
    for t, dt, p in ev:
        a += dt / ks[int(t // 900)]; ts.append(t); As.append(a)
    return ts, As, ks


def solved_at(d, G, secs):
    t0 = os.stat(f'{L}/{d}/config.json').st_mtime
    ms = sorted(os.stat(f'{L}/{d}/hints/' + g).st_mtime - t0 for g in os.listdir(f'{L}/{d}/hints') if g in G)
    return [bisect.bisect_right(ms, s) for s in secs]


def main():
    a = sys.argv[1:]
    at = [60, 120, 180, 240, 300]
    if '--at' in a:
        i = a.index('--at'); at = [float(x) for x in a[i + 1].split(',')]; del a[i:i + 2]
    G = {l.strip() for l in open(a[0]) if l.strip()}
    ref, arms = a[1], a[1:]
    C = {d: acurve(d) for d in arms}
    rts, rAs, _ = C[ref]
    targets = []
    for m in at:
        i = bisect.bisect_right(rts, m * 60) - 1
        targets.append(rAs[i] if i >= 0 else 0.0)
    print(f'reference {ref}: abstract worker hours at ' + ', '.join(f'{m:g} min {x / 3600:.1f}' for m, x in zip(at, targets)))
    for d in arms:
        ts, As, ks = C[d]
        secs = []
        for x in targets:
            j = bisect.bisect_left(As, x)
            secs.append(ts[j] if j < len(ts) else float('nan'))
        sv = solved_at(d, G, [s if s == s else 1e12 for s in secs])
        kk = ' '.join(f'{ks[b]:.2f}' for b in sorted(ks)[:21:4])
        print(f'{d:5} ' + '  '.join(f'{m:g}:{(s / 60 if s == s else float("nan")):.0f}m {v}' for m, s, v in zip(at, secs, sv))
              + f'   (CPU s per abstract s by hour: {kk})')


if __name__ == '__main__':
    main()
