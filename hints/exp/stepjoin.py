#!/usr/bin/env python3
"""(20 Nov 10:50) Proofs from cross-theory step joins (exp/joincheck.py; notes/2026-11-20-p9-negation-bug.md, 'join').

joincheck finds unsolved goals whose ground equation rewrites to one normal form with the proof steps of proven unit
goals of theories within the goal's (each step a theorem of the goal's theory, when the source proof is sound). This
gives twee those steps as lemma axioms, named skax_<i>_<source goal> (transfer.py reads the .ax file's third
column), so the kept output's USEDAXIOMS records which proofs the new one rests on (exp/trust.py). The steps are also
the hints. Production's transfer options, --keep-out, proofs into loops/UL.

  stepjoin.py DIR JOIN.tsv... [-j 2] [--time 20] [--trusted OUT.trusted] [--nonjoined N [--seed 1]]

--nonjoined N (20 Nov 10:55): N goals that did not join instead, with the steps that rewrote their sides (the
normal forms differ; are the steps useful lemmas anyway?). --no-steps: the same goals without the steps (control).

(20 Nov 11:14) Every step axiom must hold in the theory's Mace4 models (exp/modelcheck.py; models cached in
loops/MODELCHECK/models), or the goal is skipped: hints files also hold printed goal terms such as
'm(r(X0,X1,X2),X3) = m(r(X0,X1,X2),...)', not theorems, which joincheck's rewriter could take as rules
(notes/2026-11-20-model-audit.md).
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/project/twee/hints')

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
    NJ, seed = int(val('--nonjoined', '0')), int(val('--seed', '1'))
    nosteps = '--no-steps' in a
    a = [x for x in a if x != '--no-steps']
    d, files = os.path.abspath(a[0]), a[1:]
    TR = {l.strip() for l in open(tr) if l.strip()} if tr else None
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    done = set()
    if os.path.exists(os.path.join(d, 'transfer.tsv')):
        done = {l.split('\t')[0] for l in open(os.path.join(d, 'transfer.tsv'))}
    os.makedirs(d, exist_ok=True)
    rows, lines = [], {}
    import modelcheck, p9twee
    from joincheck import parse
    MD = os.path.join(L, 'MODELCHECK', 'models')
    models, nfalse = {}, 0
    for p in files:
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) < 5 or w[1] != ('0' if NJ else '1') or not w[4] or w[0] in S or w[0] in done:
                continue
            steps = []
            for t in w[4].split(','):
                sg, _, i = t.rpartition(':')
                if sg in ('axiom', 'hyp') or not sg:   # (the theory's axioms; a goal's own hypothesis)
                    continue
                # (20 Nov 12:38) joincheck --banks: 'LOOP:goal', a step of that loop's proof of the goal
                bk, _, g2 = sg.rpartition(':')
                bk = bk or 'UL'
                if TR is not None and g2 not in TR:
                    steps = None; break
                if sg not in lines:
                    lines[sg] = open(os.path.join(L, bk, 'hints', g2)).read().split('\n')
                x = lines[sg][int(i)].split('\t')
                steps.append((x[0], x[1], g2))
            if steps is None:
                continue
            ax = p9twee.tptp_parts(w[0])[0]
            key = modelcheck.theory_key(ax)
            if key not in models:
                os.makedirs(MD, exist_ok=True)
                modelcheck.mace((key, ax, os.path.dirname(MD)))
                models[key] = modelcheck.read_models(os.path.join(MD, key + '.out'))
            if any(modelcheck.holds(parse(l), parse(r), models[key]) is not None for l, r, _ in steps):
                nfalse += 1
                print(f'  {w[0]}: a step is false in a model of its theory, skipped', flush=True)
                continue
            gd = os.path.join(d, w[0])
            os.makedirs(gd, exist_ok=True)
            sk = os.path.join(gd, 'steps')
            with open(sk, 'w') as f:
                f.writelines(f'{l}\t{r}\n' for l, r, _ in steps if not nosteps)
            with open(sk + '.ax', 'w') as f:
                f.writelines(f'{l}\t{r}\t{sg}\n' for l, r, sg in steps if not nosteps)
            rows.append(f'{w[0]}\t{sk}\t0\n')
    if NJ:
        import random
        random.Random(seed).shuffle(rows)
        rows = rows[:NJ]
    print(f'{len(rows)} {"non-joined" if NJ else "joined"} goals to prove ({nfalse} skipped for a false step)', flush=True)
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
