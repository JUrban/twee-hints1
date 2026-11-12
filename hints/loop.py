#!/usr/bin/env python3
"""Veroff-style hint loop for twee on AIM60k.

Round 0 runs every problem of the set without hints (unless --init DIR
imports an earlier loop's state). Each later round runs every unsolved
problem with a pool of hints taken from the proofs found so far, and adds
the proofs it finds to the pool.

usage: loop.py SET DIR [--rounds N] [--timeout S] [-j N] [--twee BIN]
               [--args "..."] [--pool original|all] [--aux]
"""
import argparse, collections, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib
import given as givenlib

VENV_PY = '/project/hintwork/venv/bin/python'

PROB = hintlib.PROB

def orig_of(name):
    return name.split('__goal_')[0]

def canon_key(l, r, sig):
    a = hintlib.generalize(l, r, sig)
    b = hintlib.generalize(r, l, sig)
    return min(a, b)

class Loop:
    def __init__(self, a):
        self.a = a
        self.dir = a.dir
        os.makedirs(os.path.join(self.dir, 'hints'), exist_ok=True)
        os.makedirs(os.path.join(self.dir, 'tmp'), exist_ok=True)
        os.makedirs(os.path.join(self.dir, 'given'), exist_ok=True)
        self.model = None  # (model, vocab, goaldir) of the current round
        self.names = [l.strip() for l in open(a.set) if l.strip()]
        self.sig = {}
        self.solved = {}   # name -> (round, time)
        sp = os.path.join(self.dir, 'solved.tsv')
        if os.path.exists(sp):
            for l in open(sp):
                n, r, t = l.split('\t')[:3]
                self.solved[n] = (int(r), float(t))

    def signature(self, name):
        o = orig_of(name)
        if o not in self.sig:
            self.sig[o] = hintlib.problem_signature(name)
        return self.sig[o]

    def hints_of(self, name):
        p = os.path.join(self.dir, 'hints', name)
        if not os.path.exists(p):
            return []
        return [tuple(l.rstrip('\n').split('\t')) for l in open(p) if '\t' in l]

    def build_pools(self):
        """pool key -> list of (l, r), most frequent first."""
        cnt = collections.defaultdict(collections.Counter)
        for n in self.solved:
            key = orig_of(n) if self.a.pool == 'original' else 'all'
            for h in self.hints_of(n):
                cnt[key][h] += 1
        return {k: [h for h, _ in c.most_common()] for k, c in cnt.items()}

    def timeout(self, rnd):
        ts = [float(x) for x in str(self.a.timeout).split(',')]
        return ts[min(rnd, len(ts) - 1)]

    def train_model(self, rnd):
        """Train the rule model on all given logs so far; write goal files for the unsolved."""
        a = self.a
        mdir = os.path.join(self.dir, 'models'); os.makedirs(mdir, exist_ok=True)
        m = os.path.join(mdir, 'r%d.txt' % rnd); v = m + '.vocab'
        dirs = [os.path.join(self.dir, 'given')] + (a.given_extra.split(',') if a.given_extra else [])
        t0 = time.time()
        if a.model_fixed:
            m, v = a.model_fixed.split(',')
        else:
          subprocess.run([VENV_PY, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rulemodel.py'),
                        ','.join(dirs), '--all', '--ntest', '0', '--save', m, '--vocab', v],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env=dict(os.environ, OMP_NUM_THREADS='8'))
        import rulemodel
        vocab = {}
        for line in open(v):
            c, k = line.rstrip('\n').split('\t'); vocab[k] = int(c)
        gdir = os.path.join(self.dir, 'goals', 'r%d' % rnd); os.makedirs(gdir, exist_ok=True)
        for n in self.names:
            if n not in self.solved:
                rulemodel.write_goalfile(n, vocab, os.path.join(gdir, n))
        self.model = (m, v, gdir)
        print(f'  round {rnd}: trained rule model {time.time()-t0:.0f}s', file=sys.stderr, flush=True)

    def run_one(self, name, hints, rnd):
        a = self.a
        path = os.path.join(PROB, name + '.p')
        cmd = [a.twee, path, '--max-time', str(self.timeout(rnd)), '--no-colour', '--quiet',
               '--no-proof', '--print-hints', '--print-given'] + a.args.split()
        if self.model:
            m, v, gdir = self.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, name)] + \
                   a.model_args.split()
        if hints and a.stall:
            cmd += ['--eqhint-stall', str(a.stall)]
        if hints:
            hpath = os.path.join(self.dir, 'tmp', name + '.hints')
            with open(hpath, 'w') as f:
                for l, r in hints:
                    f.write(f'{l}\t{r}\n')
            cmd += ['--hints-file', hpath]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=self.timeout(rnd) + 30)
            out = p.stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b'').decode('utf8', 'replace') + '\nKILLED\n'
        dt = time.time() - t0
        if hints:
            os.unlink(hpath)
        ok = 'HINTS-END' in out
        stats = ''
        for line in out.splitlines():
            if line.startswith('HINTSTATS'):
                stats = line
        res = None
        if ok:
            L, G = hintlib.extract_hints(out)
            sig = self.signature(name)
            seen, hs = set(), []
            for l, r in L + G:
                if l == r:
                    continue
                k = canon_key(l, r, sig)
                if k[0] == k[1] or k in seen:
                    continue
                seen.add(k); hs.append(k)
            if self.a.aux:
                for l, r in hintlib.extract_aux(out):
                    k = canon_key(l, r, sig)
                    if k[0] == k[1] or k in seen:
                        continue
                    seen.add(k); hs.append(k)
            ax = set(givenlib.key(l, r, sig) for l, r in givenlib.axioms(name))
            pos = set(givenlib.key(l, r, sig) for l, r in L + G)
            rows = []
            for idx, x in enumerate(givenlib.parse_given_parents(out)):
                if x is None or x[0] == x[1]:
                    continue
                l, r, p1, p2 = x
                k = givenlib.key(l, r, sig)
                lab = -1 if k in ax else (1 if k in pos else 0)
                rows.append(f'{lab}\t{idx}\t{k[0]}\t{k[1]}\t{p1}\t{p2}\n')
            with open(os.path.join(self.dir, 'given', name), 'w') as gf:
                gf.writelines(rows)
            res = hs
        return name, ok, dt, stats, res

    def hints_for(self, n, pools, knn):
        a = self.a
        if a.pool.startswith('knn'):
            _, k, topn = a.pool.split(':')
            return [tuple(h.split('\t')) for h in knn.select(n, int(k), int(topn))]
        key = orig_of(n) if a.pool == 'original' else 'all'
        return pools.get(key, [])[:a.max_hints]

    def round(self, rnd):
        a = self.a
        todo = [n for n in self.names if n not in self.solved]
        pools = {}
        knn = None
        hinted = rnd > 0 or (a.hints_extra and a.hints_from_start)
        if hinted:
            if a.pool.startswith('knn'):
                import hintsel
                knn = hintsel.KNN(os.path.join(self.dir, 'hints'), list(self.solved))
                for d in (a.hints_extra.split(',') if a.hints_extra else []):
                    for f in os.listdir(d):
                        if f not in knn.hints:
                            L = [l.rstrip('\n') for l in open(os.path.join(d, f)) if '\t' in l]
                            if L:
                                knn.add(f, L)
            else:
                pools = self.build_pools()
        if a.model and (rnd > 0 or a.given_extra or a.model_fixed):
            self.train_model(rnd)
        rdir = os.path.join(self.dir, 'r%d' % rnd)
        os.makedirs(rdir, exist_ok=True)
        t0 = time.time(); new = 0
        with open(os.path.join(rdir, 'results.tsv'), 'w') as rf, \
             open(os.path.join(self.dir, 'solved.tsv'), 'a') as sf, \
             ThreadPoolExecutor(a.j) as ex:
            futs = []
            for n in todo:
                hints = self.hints_for(n, pools, knn) if hinted else []
                if rnd > 0 and not hints and not a.rerun_unhinted:
                    continue
                futs.append(ex.submit(self.run_one, n, hints, rnd))
            for k, f in enumerate(as_completed(futs)):
                n, ok, dt, stats, hs = f.result()
                rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{stats}\n'); rf.flush()
                if ok:
                    new += 1
                    self.solved[n] = (rnd, dt)
                    sf.write(f'{n}\t{rnd}\t{dt:.2f}\n'); sf.flush()
                    with open(os.path.join(self.dir, 'hints', n), 'w') as hf:
                        for l, r in hs:
                            hf.write(f'{l}\t{r}\n')
                if (k + 1) % 200 == 0:
                    print(f'  round {rnd}: {k+1}/{len(futs)} new={new} {time.time()-t0:.0f}s',
                          file=sys.stderr, flush=True)
        msg = (f'round {rnd}: ran {len(futs)} new {new} total {len(self.solved)}/{len(self.names)} '
               f'{time.time()-t0:.0f}s')
        print(msg, file=sys.stderr, flush=True)
        with open(os.path.join(self.dir, 'log.txt'), 'a') as lf:
            lf.write(msg + '\n')
        return new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set')
    ap.add_argument('dir')
    ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--timeout', default='2', help='seconds, or a list per round: 2,8,30')
    ap.add_argument('--model', action='store_true', help='train and use the ENIGMA rule model')
    ap.add_argument('--model-args', default='--rule-threshold 0.1 --rule-penalty 2')
    ap.add_argument('--given-extra', help='more given dirs (comma-separated) for training')
    ap.add_argument('--stall', type=int, default=0, help='--eqhint-stall for hinted runs')
    ap.add_argument('--model-fixed', help='MODEL,VOCAB: use this rule model in every round (no retraining)')
    ap.add_argument('--hints-extra', help='more hint dirs (comma-separated) for the kNN pool')
    ap.add_argument('--hints-from-start', action='store_true', help='use --hints-extra already in round 0')
    ap.add_argument('-j', type=int, default=20)
    ap.add_argument('--twee', default='/project/bin/twee')
    ap.add_argument('--args', default='--no-flatten-goal')
    ap.add_argument('--pool', default='original')
    ap.add_argument('--max-hints', type=int, default=100000)
    ap.add_argument('--aux', action='store_true')
    ap.add_argument('--rerun-unhinted', action='store_true')
    ap.add_argument('--init', help='import round-0 results (solved.tsv and hints) of another loop dir')
    a = ap.parse_args()
    if a.init and not os.path.exists(os.path.join(a.dir, 'solved.tsv')):
        import shutil
        os.makedirs(os.path.join(a.dir, 'hints'), exist_ok=True)
        with open(os.path.join(a.dir, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(a.init, 'solved.tsv')):
                if l.split('\t')[1] == '0':
                    f.write(l)
                    n = l.split('\t')[0]
                    shutil.copy(os.path.join(a.init, 'hints', n), os.path.join(a.dir, 'hints', n))
    lp = Loop(a)
    with open(os.path.join(a.dir, 'config.json'), 'w') as f:
        json.dump(vars(a), f, indent=1)
    for r in range(a.start, a.start + a.rounds):
        if lp.round(r) == 0 and r > 0:
            break

if __name__ == '__main__':
    main()
