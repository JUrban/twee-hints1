#!/usr/bin/env python3
"""(20 Nov 10:50) Proofs from cross-theory step joins (exp/joincheck.py; notes/2026-11-20-p9-negation-bug.md, 'join').

joincheck finds unsolved goals whose ground equation rewrites to one normal form with the proof steps of proven unit
goals of theories within the goal's (each step a theorem of the goal's theory, when the source proof is sound). This
gives twee those steps as lemma axioms, named skax_<i>_<source goal> (transfer.py reads the .ax file's third
column), so the kept output's USEDAXIOMS records which proofs the new one rests on (exp/trust.py). The steps are also
the hints. Production's transfer options, --keep-out, proofs into loops/UL.

  stepjoin.py DIR JOIN.tsv... [-j 2] [--time 20] [--trusted OUT.trusted]
"""
import os, subprocess, sys

L = '/project/hintwork/loops'
H = '/project/twee/hints'
OPTS = ['--model', '--model-fixed', '/project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab',
        '--model-theory', '--lemmas', '6', '--lemma-knn', '30', '--lemma-subsets', '--lemma-after', '--pool', 'original',
        '--twee', '/project/bin/twee-pg61', '--wall-factor', '15', '--keep-out',
        '--args=--abstract-time 2000 --no-eqhint-consider']


def main():
    a = sys.argv[1:]
    def val(k, dflt):
        if k in a:
            i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
        return dflt
    j, T, tr = val('-j', '2'), val('--time', '20'), val('--trusted', None)
    d, files = os.path.abspath(a[0]), a[1:]
    TR = {l.strip() for l in open(tr) if l.strip()} if tr else None
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    done = set()
    if os.path.exists(os.path.join(d, 'transfer.tsv')):
        done = {l.split('\t')[0] for l in open(os.path.join(d, 'transfer.tsv'))}
    os.makedirs(d, exist_ok=True)
    rows, lines = [], {}
    for p in files:
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) < 5 or w[1] != '1' or w[0] in S or w[0] in done:
                continue
            steps = []
            for t in w[4].split(','):
                sg, _, i = t.rpartition(':')
                if sg == 'axiom' or not sg:
                    continue
                if TR is not None and sg not in TR:
                    steps = None; break
                if sg not in lines:
                    lines[sg] = open(os.path.join(L, 'UL', 'hints', sg)).read().split('\n')
                x = lines[sg][int(i)].split('\t')
                steps.append((x[0], x[1], sg))
            if steps is None:
                continue
            gd = os.path.join(d, w[0])
            os.makedirs(gd, exist_ok=True)
            sk = os.path.join(gd, 'steps')
            with open(sk, 'w') as f:
                f.writelines(f'{l}\t{r}\n' for l, r, _ in steps)
            with open(sk + '.ax', 'w') as f:
                f.writelines(f'{l}\t{r}\t{sg}\n' for l, r, sg in steps)
            rows.append(f'{w[0]}\t{sk}\t0\n')
    print(f'{len(rows)} joined goals to prove', flush=True)
    if not rows:
        return
    gp = os.path.join(d, f'goals_{len(done)}.tsv')
    open(gp, 'w').writelines(rows)
    if not os.path.lexists(os.path.join(d, 'hints')):
        os.symlink(os.path.join(L, 'UL', 'hints'), os.path.join(d, 'hints'))
    with open(os.path.join(d, 'solved.tsv'), 'w') as f:
        for l in open(os.path.join(L, 'UL', 'solved.tsv')):
            w = l.split('\t')
            if len(w) >= 3 and l.endswith('\n') and (TR is None or w[0] in TR):
                f.write(l)
    env = dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100', OMP_NUM_THREADS='1')
    subprocess.run([sys.executable, os.path.join(H, 'transfer.py'), 'run', gp, d, '-j', j, '--time', T,
                    '--src-lemmas', '0', '--live-dst', os.path.join(L, 'UL'), '--'] + OPTS, env=env)


if __name__ == '__main__':
    main()
