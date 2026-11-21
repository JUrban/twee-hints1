#!/usr/bin/env python3
"""(21 Nov 05:10) exp49 (notes/2026-11-21-quick-first.md): the first pass of loop.py --quick arms against controls.

  quickstat.py DIR... [--bins 15,30,60,90,120,180,240,300]

Per arm (loops/<DIR>/r1/results.tsv): when the first pass ended (the last goal's first fresh run: a q=1 row in a
--quick arm, else the goal's first L0 row), the quick runs' proofs and failures, the first T0 runs of goals whose
quick run failed (proved, failed, by half hour), and per time bin: fresh first runs (proved/run), T0 runs of
quick-failed goals, failed-before retries at L0, deeper runs, with their CPU hours.
"""
import collections, sys

L = '/project/hintwork/loops'


def main():
    a = sys.argv[1:]
    bins = [15, 30, 60, 90, 120, 180, 240, 300]
    if '--bins' in a:
        i = a.index('--bins'); bins = [int(x) for x in a[i + 1].split(',')]; del a[i:i + 2]
    for d in a:
        rows = [l.rstrip('\n').split('\t') for l in open(f'{L}/{d}/r1/results.tsv') if l.strip()]
        t = lambda w: float(next(x for x in w if x.startswith('t='))[2:])
        seen, qf = set(), set()
        kinds = collections.defaultdict(lambda: [0, 0, 0.0])   # (bin, kind) -> proved, runs, CPU s
        endfirst = 0.0
        q = [0, 0]; qt0 = [0, 0]
        for w in rows:
            n, ok, dt, lab = w[0], w[1] == 'THM', float(w[2]), w[4]
            tt = t(w); b = next((x for x in bins if tt <= 60 * x), 'later')
            quick = 'q=1' in w[7:]
            if quick:
                k = 'quick'; q[0] += ok; q[1] += 1
                if not ok:
                    qf.add(n)
            elif lab == 'L0' and n not in seen:
                k = 'first'
            elif lab == 'L0' and n in qf:
                k = 'T0 after quick'; qf.discard(n); qt0[0] += ok; qt0[1] += 1
            elif lab == 'L0':
                k = 'retry'
            else:
                k = 'deep'
            if lab == 'L0' and n not in seen:
                endfirst = tt
            seen.add(n)
            v = kinds[(b, k)]; v[0] += ok; v[1] += 1; v[2] += dt
        print(f'== {d}: {len(rows)} runs; first pass ended at {endfirst / 60:.0f} min; quick runs {q[0]}/{q[1]}; '
              f'T0 runs after a failed quick run {qt0[0]}/{qt0[1]}, {len(qf)} still waiting')
        ks = ['quick', 'first', 'T0 after quick', 'retry', 'deep']
        print('  min  | ' + ' | '.join(f'{k:>22}' for k in ks))
        for b in bins + ['later']:
            cells = []
            for k in ks:
                v = kinds.get((b, k))
                cells.append(f'{v[0]:>6}/{v[1]:<6} {v[2] / 3600:5.1f}h' if v else ' ' * 22)
            if any(c.strip() for c in cells):
                print(f'  {b!s:>5} | ' + ' | '.join(f'{c:>22}' for c in cells))


if __name__ == '__main__':
    main()
