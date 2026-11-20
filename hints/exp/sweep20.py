#!/usr/bin/env python3
"""(20 Nov 14:25) One fresh 20 s run for each unsolved goal that production never ran above 5 s
(notes/2026-11-20-sweep20.md).

The non-joined steps test (notes/2026-11-20-step-join.md) proved 4 of 100 unsolved goals in both arms, with and
without the steps: production's transfer options at 20 s with today's lemma context. Production had run those 4
goals 20-80 times, every run at 5 s (L0 and the 5 s variants). 2,895 of the 3,606 unsolved goals never had a
production run above 5 s.

The goals in random order (--seed), in chunks of --chunk. Before each chunk: exp/trust.py over production, and the
chunk's lemma context is production's trusted solved list at that moment (so new proofs, the sweep's own included,
are lemmas for the later chunks). Each chunk is one `transfer.py run` with exp/stepjoin.py's options (production's
transfer options, --keep-out, so every proof has its USEDAXIOMS record), no hints, proofs into loops/UL.

  sweep20.py DIR GOALS.txt [-j 4] [--time 20] [--chunk 300] [--seed 1] [--exposed ORIGINALS.txt]
DIR/J, if present, overrides -j for the next chunk. Results: DIR/c<k>/transfer.tsv; DIR/sweep.tsv (chunk, goal,
status, seconds).
"""
import os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/project/twee/hints')
from stepjoin import OPTS, L, H


def main():
    a = sys.argv[1:]
    def val(k, d):
        if k in a:
            i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
        return d
    j, T, chunk, seed = val('-j', '4'), val('--time', '20'), int(val('--chunk', '300')), int(val('--seed', '1'))
    ex = val('--exposed', os.path.join(L, 'UNSOUND', 'exposed.txt'))
    d, gf = os.path.abspath(a[0]), a[1]
    os.makedirs(d, exist_ok=True)
    goals = sorted({l.strip() for l in open(gf) if l.strip()})
    random.Random(seed).shuffle(goals)
    empty = os.path.join(d, 'empty')
    open(empty, 'w').close()
    done = set()
    sp = os.path.join(d, 'sweep.tsv')
    if os.path.exists(sp):
        done = {l.split('\t')[1] for l in open(sp) if l.strip()}
    k = 0
    while True:
        S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv')) if l.strip()}
        todo = [g for g in goals if g not in done and g not in S][:chunk]
        if not todo:
            break
        while os.path.exists(os.path.join(d, f'c{k}')):
            k += 1
        cd = os.path.join(d, f'c{k}')
        os.makedirs(cd)
        tp = os.path.join(cd, 'trust')
        env = dict(os.environ, OMP_NUM_THREADS='1')
        subprocess.run([sys.executable, os.path.join(H, 'exp', 'trust.py'), tp, '-j', '2', '--exposed', ex],
                       env=env, check=True, stdout=open(tp + '.log', 'w'), stderr=subprocess.STDOUT)
        TR = {l.strip() for l in open(tp + '.trusted') if l.strip()}
        with open(os.path.join(cd, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(L, 'UL', 'solved.tsv')):
                w = l.split('\t')
                if len(w) >= 3 and l.endswith('\n') and w[0] in TR:
                    f.write(l)
        os.symlink(os.path.join(L, 'UL', 'hints'), os.path.join(cd, 'hints'))
        gp = os.path.join(cd, 'goals.tsv')
        open(gp, 'w').writelines(f'{g}\t{empty}\t0\n' for g in todo)
        jj = open(os.path.join(d, 'J')).read().strip() if os.path.exists(os.path.join(d, 'J')) else j
        print(f'chunk {k}: {len(todo)} goals, {len(TR)} trusted lemma sources, -j {jj}', flush=True)
        env = dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100',
                   OMP_NUM_THREADS='1')
        subprocess.run([sys.executable, os.path.join(H, 'transfer.py'), 'run', gp, cd, '-j', jj, '--time', T,
                        '--src-lemmas', '0', '--live-dst', os.path.join(L, 'UL'), '--'] + OPTS, env=env,
                       stdout=open(os.path.join(cd, 'run.log'), 'w'), stderr=subprocess.STDOUT)
        res = {}
        tt = os.path.join(cd, 'transfer.tsv')
        if os.path.exists(tt):
            for l in open(tt):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 3:
                    res[w[0]] = (w[1], w[2])
        with open(sp, 'a') as f:
            for g in todo:
                st, sec = res.get(g, ('-', '0'))
                f.write(f'{k}\t{g}\t{st}\t{sec}\n')
                done.add(g)
        n = sum(1 for g in todo if res.get(g, ('',))[0] == 'THM')
        tot = [l.split('\t') for l in open(sp)]
        print(f'chunk {k}: {n} of {len(todo)} proved; sweep so far {sum(1 for w in tot if w[2] == "THM")} of '
              f'{len(tot)}, {sum(float(w[3]) for w in tot) / 3600:.1f} h of run time', flush=True)
        k += 1
    print('sweep20: done', flush=True)


if __name__ == '__main__':
    main()
