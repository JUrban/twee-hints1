#!/usr/bin/env python3
"""Veroff-style hint loop with Prover9 (control for the twee loop).

p9loop.py NAMES DIR [--timeout 2,2,2,8] [-j N] [--prover9 BIN]
Round 0 runs every problem without hints. Each later round runs the
unsolved problems with hints: the positive steps of the proofs of all
solved goals of the same original (Prover9's default hint handling),
skolem constants c1, c2, ... generalised to variables.
"""
import argparse, collections, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

LADR = '/project/AIM60k/problems/ladr'
_line = re.compile(r'^(\d+) (.*?)\.\s+\[(.*)\]\.\s*$')

def proof_hints(out):
    i = out.find('= PROOF ='); j = out.find('= end of proof =')
    if i < 0 or j < 0:
        return []
    hs = []
    for line in out[i:j].splitlines():
        m = _line.match(line.strip())
        if not m:
            continue
        cl, just = m.group(2), m.group(3)
        cl = cl.split(' # ')[0].strip()
        if just.startswith(('assumption', 'deny')) or '!=' in cl or '|' in cl or cl == '$F':
            continue
        hs.append(re.sub(r'\bc(\d+)\b', r'vc\1', cl))
    return hs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('dir')
    ap.add_argument('--timeout', default='2,2,2,8')
    ap.add_argument('-j', type=int, default=3)
    ap.add_argument('--prover9', default='/project/bin/prover9-new')
    a = ap.parse_args()
    ts = [float(x) for x in a.timeout.split(',')]
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    for d in ('hints', 'tmp'):
        os.makedirs(os.path.join(a.dir, d), exist_ok=True)
    solved = {}

    def run(name, hints, t):
        files = [os.path.join(LADR, name)]
        hp = None
        if hints:
            hp = os.path.join(a.dir, 'tmp', name + '.hints')
            with open(hp, 'w') as f:
                f.write('formulas(hints).\n' + ''.join(h + '.\n' for h in hints) + 'end_of_list.\n')
            files.append(hp)
        t0 = time.time()
        try:
            out = subprocess.run([a.prover9, '-t', str(t), '-f'] + files, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, timeout=t + 30).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired:
            out = ''
        dt = time.time() - t0
        if hp:
            os.unlink(hp)
        return name, 'THEOREM PROVED' in out, dt, proof_hints(out) if 'THEOREM PROVED' in out else []

    log = open(os.path.join(a.dir, 'log.txt'), 'a')
    for rnd, t in enumerate(ts):
        pools = collections.defaultdict(collections.Counter)
        for n, hs in solved.items():
            for h in hs:
                pools[n.rsplit('__goal_', 1)[0]][h] += 1
        todo = [n for n in names if n not in solved]
        t0 = time.time(); new = 0
        with ThreadPoolExecutor(a.j) as ex, open(os.path.join(a.dir, f'r{rnd}.tsv'), 'w') as rf:
            futs = []
            for n in todo:
                hints = [h for h, _ in pools[n.rsplit('__goal_', 1)[0]].most_common()] if rnd > 0 else []
                if rnd > 0 and not hints:
                    continue
                futs.append(ex.submit(run, n, hints, t))
            for f in as_completed(futs):
                n, ok, dt, hs = f.result()
                rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\n')
                if ok:
                    new += 1; solved[n] = hs
                    with open(os.path.join(a.dir, 'hints', n), 'w') as hf:
                        hf.write(''.join(h + '\n' for h in hs))
        msg = f'round {rnd} ({t:g} s): ran {len(futs)} new {new} total {len(solved)}/{len(names)} {time.time()-t0:.0f}s'
        print(msg, flush=True); log.write(msg + '\n'); log.flush()

if __name__ == '__main__':
    main()
