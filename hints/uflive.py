#!/usr/bin/env python3
"""Unfolded-twee side worker for a running loop (15 Nov).

Twee's KBO folds the AIM definitions (a, k, l, r, t); Prover9 unfolds them. With the definitions
substituted away (loop.py --unfold), twee proves 7 of the 9 goals Prover9's side worker proved
(folded twee: 2) and 3 of the first 10 that Prover9 failed. This worker replaces p9twee.py --live.

Each cycle:
  1. sync: rows of LOOPDIR/solved.tsv that SIDEDIR lacks are appended to SIDEDIR/solved.tsv as
     round 0, with their hints files;
  2. targets: as p9twee.py --live, the goals the loop is stalled on (in its latest round the last
     run failed and was not fresh, and a fresh run failed too), at most --max-lgap proof lines from
     the nearest proven goal below, nearest first; a goal tried before comes back only when its
     nearest proven goal below changed or its original's proven-goal count grew by --retry-grow;
     at most --batch goals;
  3. one round of loop.py --unfold on them in SIDEDIR (round C, --loop-args);
  4. merge.py LOOPDIR SIDEDIR: the new proofs go into the loop (it reads them with --sync).

  python3 uflive.py LOOPDIR SIDEDIR [-j 4] [--batch 24] [--loop-args '...']
"""
import argparse, glob, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
GOAL_LINES = '/project/hintwork/abs/goal_lines.tsv'


def split(n):
    o, _, k = n.rpartition('__goal_')
    return o, int(k)


def rows(path):
    out = {}
    if os.path.exists(path):
        for l in open(path):
            if l.endswith('\n'):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 2:
                    out.setdefault(w[0], w)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('loopdir'); ap.add_argument('sidedir')
    ap.add_argument('-j', type=int, default=4)
    ap.add_argument('--batch', type=int, default=24)
    ap.add_argument('--max-lgap', type=int, default=80)
    ap.add_argument('--retry-grow', type=float, default=1.25)
    ap.add_argument('--unfold', default='all')
    ap.add_argument('--loop-args', default='')
    ap.add_argument('--twee-args', default='', help="loop.py --args (twee's arguments, one string)")
    ap.add_argument('--cycles', type=int, default=10 ** 6)
    a = ap.parse_args()
    D, U = a.loopdir, a.sidedir
    os.makedirs(os.path.join(U, 'hints'), exist_ok=True)
    gl = {l.split()[0]: int(l.split()[1]) for l in open(GOAL_LINES)}
    tpath = os.path.join(U, 'tried.tsv')
    tried = {}   # goal -> (nearest proven goal below, proven goals of its original) at its last try
    if os.path.exists(tpath):
        for l in open(tpath):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 3:
                tried[w[0]] = (w[1], int(w[2]))
    C = max([int(p.split('/')[-2][1:]) for p in glob.glob(os.path.join(U, 'r*', 'results.tsv'))] + [0]) + 1
    for _ in range(a.cycles):
        t0 = time.time()
        # 1. sync
        S = rows(os.path.join(D, 'solved.tsv'))
        have = rows(os.path.join(U, 'solved.tsv'))
        nsync = 0
        with open(os.path.join(U, 'solved.tsv'), 'a') as f:
            for n, w in S.items():
                if n in have:
                    continue
                h = os.path.join(D, 'hints', n)
                if not os.path.exists(h):
                    continue
                shutil.copy(h, os.path.join(U, 'hints', n))
                f.write(f'{n}\t0\t{w[2] if len(w) > 2 else "0"}\n'); nsync += 1
        # 2. targets
        byo = {}
        for n in S:
            o, k = split(n); byo.setdefault(o, set()).add(k)

        def below(n):
            o, k = split(n)
            b = [j for j in byo.get(o, ()) if j < k]
            return f'{o}__goal_{max(b)}' if b else ''

        def lgap(n):
            b = below(n)
            return gl[n] - gl[b] if b and n in gl and b in gl else 10 ** 6

        rfs = sorted(glob.glob(os.path.join(D, 'r*', 'results.tsv')), key=lambda p: int(p.split('/')[-2][1:]))
        last, fresh = {}, set()
        for l in open(rfs[-1]):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5:
                last[w[0]] = (w[1], w[4])
                if w[4] == 'L0':
                    fresh.add(w[0])
        todo = []
        for n, (ok, lev) in last.items():
            if ok != 'NO' or lev == 'L0' or n not in fresh or n in S or lgap(n) > a.max_lgap:
                continue
            if n in tried:
                b, c = tried[n]
                if b == below(n) and len(byo.get(split(n)[0], ())) < a.retry_grow * max(c, 1):
                    continue
            todo.append(n)
        todo = sorted(todo, key=lambda n: (lgap(n), n))[:a.batch]
        print(f'cycle {C}: synced {nsync}, {len(todo)} targets ({time.strftime("%T")})', flush=True)
        if not todo:
            time.sleep(600)
            continue
        names = os.path.join(U, f'targets.{C}')
        open(names, 'w').write(''.join(n + '\n' for n in todo))
        # 3. one round
        cmd = [sys.executable, '-u', os.path.join(HERE, 'loop.py'), names, U, '--start', str(C), '--rounds', '1',
               '-j', str(a.j), '--unfold', a.unfold] + a.loop_args.split() + \
              ([f'--args={a.twee_args}'] if a.twee_args else [])
        with open(os.path.join(U, 'loop.log'), 'a') as lf:
            subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
        res = rows(os.path.join(U, f'r{C}', 'results.tsv'))
        with open(tpath, 'a') as f:
            for n in todo:
                o, _ = split(n)
                tried[n] = (below(n), len(byo.get(o, ())))
                f.write(f'{n}\t{tried[n][0]}\t{tried[n][1]}\t{C}\t{res.get(n, ["", "?"])[1]}\n')
        # 4. merge
        m = subprocess.run([sys.executable, os.path.join(HERE, 'merge.py'), D, U], stdout=subprocess.PIPE)
        last_line = m.stdout.decode().strip().splitlines()[-1:] or ['']
        nthm = sum(1 for w in res.values() if w[1] == 'THM')
        print(f'cycle {C}: {nthm}/{len(todo)} proved, {last_line[0]}, {time.time() - t0:.0f}s', flush=True)
        C += 1


if __name__ == '__main__':
    main()
