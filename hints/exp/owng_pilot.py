#!/usr/bin/env python3
"""(20 Nov 11:32) Cross-run joining pilot (notes/2026-11-20-step-join.md, 'own given rules'): N unsolved unit goals
of production at T s with production's transfer options and loop.py --given-keep, so each failed run's given rules
land in DIR/given/<goal>; then exp/joincheck.py --own-given DIR/given: does the goal's own failed run plus the
trusted proof steps of weaker theories join where the steps alone did not (loops/JOIN/all_*.tsv)?

  owng_pilot.py DIR [-n 30] [--time 60] [-j 2] [--seed 1] [--trusted OUT.trusted]
"""
import os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/project/twee/hints')
from gensat import unit
from stepjoin import OPTS, L, H


def main():
    a = sys.argv[1:]
    def val(k, d):
        return type(d)(a[a.index(k) + 1]) if k in a else d
    d = os.path.abspath(a[0]); n = val('-n', 30); T = val('--time', 60.0); j = val('-j', 2); seed = val('--seed', 1)
    tr = val('--trusted', '')
    os.makedirs(d, exist_ok=True)
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    U = sorted(g for g in names if g not in S and unit(g))
    random.Random(seed).shuffle(U)
    U = U[:n]
    open(os.path.join(d, 'empty'), 'w').close()
    gp = os.path.join(d, 'goals.tsv')
    open(gp, 'w').writelines(f'{g}\t{os.path.join(d, "empty")}\t0\n' for g in U)
    if not os.path.lexists(os.path.join(d, 'hints')):
        os.symlink(os.path.join(L, 'UL', 'hints'), os.path.join(d, 'hints'))
    TR = {l.strip() for l in open(tr) if l.strip()} if tr else None
    with open(os.path.join(d, 'solved.tsv'), 'w') as f:
        for l in open(os.path.join(L, 'UL', 'solved.tsv')):
            w = l.split('\t')
            if len(w) >= 3 and l.endswith('\n') and (TR is None or w[0] in TR):
                f.write(l)
    env = dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100', OMP_NUM_THREADS='1')
    subprocess.run([sys.executable, os.path.join(H, 'transfer.py'), 'run', gp, d, '-j', str(j), '--time', str(T),
                    '--src-lemmas', '0', '--live-dst', os.path.join(L, 'UL'), '--'] + OPTS +
                   ['--given-keep', os.path.join(d, 'given')], env=env)
    cmd = [sys.executable, os.path.join(H, 'exp', 'joincheck.py'), os.path.join(d, 'join.tsv'), '-n', '100000',
           '--own-given', os.path.join(d, 'given')] + (['--trusted', tr] if tr else [])
    subprocess.run(cmd, env=env)


if __name__ == '__main__':
    main()
