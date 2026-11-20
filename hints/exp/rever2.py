#!/usr/bin/env python3
"""(20 Nov 10:40) Re-prove production's untrusted roots with a trusted context (notes/2026-11-20-p9-negation-bug.md).

Each pass: exp/trust.py over production's solved set; the goals are its roots (untrusted for want of a lemma record)
and the quarantined goals still unsolved (loops/UNSOUND/Q.txt); the lemma context is the trusted proofs only (the
pass dir's solved.tsv); each goal's last proof (or its quarantined one) is its hints file; production's transfer
options at --time T, --keep-out (the outputs are the new proofs' records); proofs into loops/UL. Passes until one
proves nothing new; then one at 5 T. Workers: the number in DIR/J (read each pass).

  rever2.py DIR [--time 60] [--passes 8]
"""
import os, subprocess, sys, time
L = '/project/hintwork/loops'
H = '/project/twee/hints'
OPTS = ['--model', '--model-fixed', '/project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab',
        '--model-theory', '--lemmas', '6', '--lemma-knn', '30', '--lemma-subsets', '--lemma-after', '--pool', 'original',
        '--twee', '/project/bin/twee-pg61', '--wall-factor', '15', '--keep-out',
        '--args=--abstract-time 2000 --no-eqhint-consider']


def main():
    d = os.path.abspath(sys.argv[1])
    T = float(sys.argv[sys.argv.index('--time') + 1]) if '--time' in sys.argv else 60.0
    P = int(sys.argv[sys.argv.index('--passes') + 1]) if '--passes' in sys.argv else 8
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100', OMP_NUM_THREADS='1')
    Q = {l.strip() for l in open(os.path.join(L, 'UNSOUND', 'Q.txt')) if l.strip()}
    last = False
    for p in range(1, P + 2):
        tp = os.path.join(d, f'trust{p}')
        subprocess.run([sys.executable, os.path.join(H, 'exp', 'trust.py'), tp, '-j', '4'], env=env, check=True)
        roots = [l.strip() for l in open(tp + '.roots') if l.strip()]
        trusted = {l.strip() for l in open(tp + '.trusted') if l.strip()}
        S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
        goals = sorted(set(roots) | (Q - S))
        pd = os.path.join(d, f'p{p}')
        os.makedirs(pd, exist_ok=True)
        if not os.path.lexists(os.path.join(pd, 'hints')):
            os.symlink(os.path.join(L, 'UL', 'hints'), os.path.join(pd, 'hints'))
        with open(os.path.join(pd, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(L, 'UL', 'solved.tsv')):
                if l.split('\t')[0] in trusted:
                    f.write(l)
        gp = os.path.join(pd, 'goals.tsv')
        with open(gp, 'w') as f:
            for g in goals:
                h = os.path.join(L, 'UL', 'hints', g)
                if not os.path.exists(h):
                    h = os.path.join(L, 'UNSOUND', 'qhints', g)
                f.write(f'{g}\t{h}\t0\n')
        J = open(os.path.join(d, 'J')).read().strip() if os.path.exists(os.path.join(d, 'J')) else '4'
        t = T * 5 if last else T
        print(f'pass {p} {time.strftime("%H:%M:%S")}: {len(trusted)} trusted, {len(roots)} roots, '
              f'{len(Q - S)} quarantined unsolved -> {len(goals)} goals at {t:.0f} s on {J} workers', flush=True)
        subprocess.run([sys.executable, os.path.join(H, 'transfer.py'), 'run', gp, pd, '-j', J, '--time', str(t),
                        '--src-lemmas', '0', '--live-dst', os.path.join(L, 'UL'), '--'] + OPTS, env=env,
                       stdout=open(os.path.join(pd, 'run.log'), 'w'), stderr=subprocess.STDOUT)
        n = sum(1 for l in open(os.path.join(pd, 'transfer.tsv')) if l.split('\t')[1] == 'THM') \
            if os.path.exists(os.path.join(pd, 'transfer.tsv')) else 0
        print(f'pass {p} done {time.strftime("%H:%M:%S")}: {n} proved', flush=True)
        if last:
            break
        if n == 0:
            last = True
    tp = os.path.join(d, 'trust_final')
    subprocess.run([sys.executable, os.path.join(H, 'exp', 'trust.py'), tp, '-j', '4'], env=env, check=True)
    print(f'rever2 done {time.strftime("%H:%M:%S")}', flush=True)


if __name__ == '__main__':
    main()
