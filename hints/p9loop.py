#!/usr/bin/env python3
"""Veroff-style hint loop with Prover9 (control for the twee loop).

p9loop.py NAMES DIR [--timeout 2,2,2,8 | --givens 150,150,150,600] [-j N]
          [--sfdf G] [--init DIR0] [--prover9 BIN]

Round 0 runs every problem without hints. Each later round runs the
unsolved problems with hints: the positive steps of the proofs of all
solved goals of the same original (Prover9's default hint handling),
skolem constants c1, c2, ... generalised to variables.

--givens  abstract budget per round (assign(max_given, G)) instead of
          seconds; Prover9 is deterministic, so runs repeat exactly.
--sfdf G  Veroff's reorientation: rerun each newly solved problem with its
          own proof as hints, with set(restrict_denials) (the denial only in
          the final unit conflict: strictly forward) and no demodulation
          (assign(demod_step_limit, 0), clear(back_demod)), up to G given
          clauses. If that proves the goal, its steps are the pooled hints;
          otherwise the original proof's steps are. The conversion work is
          counted in DIR/sfdf.tsv.
--convert expand|direct: reorient each new proof without search before
          pooling its hints. expand = prooftrans expand (each rewrite step
          becomes a separate step: demodulation-free); direct = LADR's
          directproof (a direct, forward proof, also expanded: SFDF).
          Each conversion's seconds and hint counts go to DIR/convert.tsv.
--hinted-sfdf: run the hinted rounds with the SFDF settings as well, so
          the intermediate steps of an expanded proof can be kept and match.
--init    take round 0 (r0.tsv and hints) from another loop dir.
Rows of rN.tsv: name, THM/NO, seconds, given clauses.
"""
import argparse, collections, os, re, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

LADR = '/project/AIM60k/problems/ladr'
_line = re.compile(r'^(\d+[A-Z]*) (.*?)\.\s+\[(.*)\]\.\s*$')
APPS = '/project/Prover9-new/apps.src'
SFDF_OPTS = 'set(restrict_denials).\nassign(demod_step_limit, 0).\nclear(back_demod).\n'

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

def proof_stats(out):
    """(steps, steps with demodulation, steps derived from the denial) of the proof."""
    i = out.find('= PROOF ='); j = out.find('= end of proof =')
    st = rw = neg = 0
    for line in out[i:j].splitlines():
        m = _line.match(line.strip())
        if not m:
            continue
        cl, just = m.group(2).split(' # ')[0], m.group(3)
        if just.startswith(('assumption', 'goal')):
            continue
        st += 1; rw += 'rewrite' in just
        neg += '!=' in cl and not just.startswith(('deny', 'copy'))
    return st, rw, neg

def givens(out):
    k = 0
    for line in out.splitlines():
        if line.startswith('given #'):
            k = int(line[7:line.index(' ', 7)])
    return k

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('dir')
    ap.add_argument('--timeout', default='2,2,2,8')
    ap.add_argument('--givens', default='')
    ap.add_argument('--sfdf', type=int, default=0)
    ap.add_argument('--init')
    ap.add_argument('--convert', choices=['expand', 'direct'])
    ap.add_argument('--hinted-sfdf', action='store_true',
                    help='run the hinted rounds with the SFDF settings too (no demodulation, denial only at the end)')
    ap.add_argument('-j', type=int, default=3)
    ap.add_argument('--prover9', default='/project/bin/prover9-new')
    a = ap.parse_args()
    budgets = [float(x) for x in (a.givens or a.timeout).split(',')]
    names = [l.split()[0] for l in open(a.names) if l.strip()]
    for d in ('hints', 'tmp', 'orig_hints'):
        os.makedirs(os.path.join(a.dir, d), exist_ok=True)
    solved = {}

    def prover9(files, budget, extra=''):
        if a.givens or extra:
            opt = os.path.join(a.dir, 'tmp', f'opt_{os.getpid()}_{time.time_ns()}.in')
            with open(opt, 'w') as f:
                f.write(extra + (f'assign(max_given, {int(budget)}).\nassign(max_seconds, 3600).\n'
                                 if a.givens or extra else ''))
            cmd = [a.prover9, '-f'] + files + [opt]
            wall = 3700
        else:
            opt = None
            cmd = [a.prover9, '-t', str(budget), '-f'] + files
            wall = budget + 30
        t0 = time.time()
        try:
            out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 timeout=wall).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired:
            out = ''
        if opt:
            os.unlink(opt)
        return out, time.time() - t0

    def write_hints(path, hints):
        with open(path, 'w') as f:
            f.write('formulas(hints).\n' + ''.join(h + '.\n' for h in hints) + 'end_of_list.\n')

    def sfdf(name, hints):
        """Reorient a proof: (hints of the SFDF proof or None, givens used, stats)."""
        hp = os.path.join(a.dir, 'tmp', name + '.own')
        write_hints(hp, hints)
        out, dt = prover9([os.path.join(LADR, name), hp], a.sfdf, SFDF_OPTS)
        os.unlink(hp)
        ok = 'THEOREM PROVED' in out
        return (proof_hints(out) if ok else None), givens(out), dt, (proof_stats(out) if ok else None)

    def convert(name, out):
        """Hints of the proof in OUT after prooftrans expand / directproof (linear time)."""
        t0 = time.time()
        tp = os.path.join(a.dir, 'tmp', name + '.out')
        with open(tp, 'w') as f:
            f.write(out)
        tool = [os.path.join(APPS, 'prooftrans'), 'expand'] if a.convert == 'expand' else [os.path.join(APPS, 'directproof')]
        try:
            conv = subprocess.run(tool + ['-f', tp], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  timeout=120).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired:
            conv = ''
        os.unlink(tp)
        hs = proof_hints(conv)
        with lock:
            cf.write(f'{name}\t{time.time() - t0:.3f}\t{len(proof_hints(out))}\t{len(hs)}\n'); cf.flush()
        if os.environ.get('P9LOOP_KEEP'):
            with open(os.path.join(a.dir, 'tmp', name + '.conv'), 'w') as f:
                f.write(conv)
        return hs

    def run(name, hints, budget):
        files = [os.path.join(LADR, name)]
        hp = None
        if hints:
            hp = os.path.join(a.dir, 'tmp', name + '.hints')
            write_hints(hp, hints)
            files.append(hp)
        out, dt = prover9(files, budget, SFDF_OPTS if hints and a.hinted_sfdf else '')
        if hp:
            os.unlink(hp)
        ok = 'THEOREM PROVED' in out
        hs = proof_hints(out) if ok else []
        if ok and a.convert:
            hs = convert(name, out) or hs
        res = [name, ok, dt, givens(out), hs, proof_stats(out) if ok else None, None]
        if ok and a.sfdf:
            res[6] = sfdf(name, hs)
        return res

    log = open(os.path.join(a.dir, 'log.txt'), 'a')
    # conversions: name, seconds (write + convert + parse), hints before, hints after
    cf = open(os.path.join(a.dir, 'convert.tsv'), 'a') if a.convert else None
    lock = threading.Lock()
    sf = open(os.path.join(a.dir, 'sfdf.tsv'), 'a') if a.sfdf else None

    def record(n, hs, st, conv):
        """Store the hints of a newly solved problem (SFDF ones when converted)."""
        with open(os.path.join(a.dir, 'orig_hints', n), 'w') as hf:
            hf.write(''.join(h + '\n' for h in hs))
        use = hs
        if conv is not None:
            sh, g, dt, sst = conv
            sf.write(f'{n}\t{"OK" if sh is not None else "FAIL"}\t{g}\t{dt:.2f}\t{st}\t{sst}\n'); sf.flush()
            if sh is not None:
                use = sh
        solved[n] = use
        with open(os.path.join(a.dir, 'hints', n), 'w') as hf:
            hf.write(''.join(h + '\n' for h in use))

    start = 0
    if a.init:
        # round 0 has no hints, so it is shared; convert its proofs if --sfdf
        shutil.copy(os.path.join(a.init, 'r0.tsv'), os.path.join(a.dir, 'r0.tsv'))
        r0 = [l.split('\t')[0] for l in open(os.path.join(a.dir, 'r0.tsv')) if '\tTHM' in l]
        def conv0(n):
            hs = [l.rstrip('\n') for l in open(os.path.join(a.init, 'orig_hints' if os.path.isdir(
                os.path.join(a.init, 'orig_hints')) else 'hints', n))]
            return n, hs, (sfdf(n, hs) if a.sfdf else None)
        with ThreadPoolExecutor(a.j) as ex:
            for n, hs, conv in ex.map(conv0, r0):
                record(n, hs, None, conv)
        start = 1
        msg = f'round 0 (from {a.init}): {len(solved)} solved'
        print(msg, flush=True); log.write(msg + '\n'); log.flush()

    for rnd in range(start, len(budgets)):
        t = budgets[rnd]
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
                n, ok, dt, g, hs, st, conv = f.result()
                rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{g}\n'); rf.flush()
                if ok:
                    new += 1
                    record(n, hs, st, conv)
        msg = f'round {rnd} ({t:g}{" givens" if a.givens else " s"}): ran {len(futs)} new {new} total {len(solved)}/{len(names)} {time.time()-t0:.0f}s'
        print(msg, flush=True); log.write(msg + '\n'); log.flush()

if __name__ == '__main__':
    main()
