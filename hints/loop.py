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
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
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
        os.makedirs(os.path.join(self.dir, 'states'), exist_ok=True)
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
            key = self.pool_key(n)
            for h in self.hints_of(n):
                cnt[key][h] += 1
        return {k: [h for h, _ in c.most_common()] for k, c in cnt.items()}

    def pool_key(self, n):
        return 'all' if self.a.pool == 'all' else orig_of(n)

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
                        ','.join(dirs), '--all', '--ntest', '0', '--save', m, '--vocab', v
                       ] + (['--theory'] if a.model_theory else []),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env=dict(os.environ, OMP_NUM_THREADS='8'))
        import rulemodel
        rulemodel.THEORY = a.model_theory
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
        if (a.lemmas or a.lemma_knn) and rnd > 0 and self.lemma_src:
            import lemmas
            if a.lemma_knn:
                txt, nl = lemmas.lemma_problem_knn(name, self.lemma_src, a.lemmas, self.lemma_index, a.lemma_knn)
            else:
                txt, nl = lemmas.lemma_problem(name, self.lemma_src, a.lemmas)
            if nl:
                path = os.path.join(self.dir, 'tmp', name + '.p')
                with open(path, 'w') as f:
                    f.write(txt)
        cmd = [a.twee, path, '--max-time', str(self.timeout(rnd)), '--no-colour', '--quiet',
               '--no-proof', '--print-hints', '--print-given'] + a.args.split()
        if self.model:
            m, v, gdir = self.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, name)] + \
                   a.model_args.split()
        if hints and a.stall:
            cmd += ['--eqhint-stall', str(a.stall)]
        spath = os.path.join(self.dir, 'states', name + '.bin')
        if a.resume:
            if os.path.exists(spath):
                cmd += ['--load-state', spath]
            cmd += ['--dump-state', spath + '.tmp']
        if hints:
            hpath = os.path.join(self.dir, 'tmp', name + '.hints')
            with open(hpath, 'w') as f:
                for h in hints:
                    f.write('\t'.join(h) + '\n')
            cmd += ['--hints-file', hpath]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=self.timeout(rnd) * (5 if "--abstract-time" in self.a.args else 1) + 30)
            out = p.stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b'').decode('utf8', 'replace') + '\nKILLED\n'
        dt = time.time() - t0
        if a.keep_out:
            od = os.path.join(self.dir, 'r%d' % rnd, 'out'); os.makedirs(od, exist_ok=True)
            i, j = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
            with open(os.path.join(od, name), 'w') as f:
                f.write(out[:i] + out[j:] if 0 <= i < j else out)  # without the given rules
        if hints:
            os.unlink(hpath)
        ok = 'HINTS-END' in out
        if a.resume:
            if ok:
                for p in (spath, spath + '.tmp'):
                    if os.path.exists(p):
                        os.unlink(p)
            elif os.path.exists(spath + '.tmp'):
                os.replace(spath + '.tmp', spath)
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
            ax = set(givenlib.key(l, r, sig) for l, r in givenlib.axioms(name, path))
            pos = set(givenlib.key(l, r, sig) for l, r in L + G + hintlib.extract_hyp(out))
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
        if path.startswith(os.path.join(self.dir, 'tmp')):
            os.unlink(path)
        return name, ok, dt, stats, res

    def hints_for(self, n, pools, knn):
        a = self.a
        if a.pool.startswith('knn'):
            _, k, topn = a.pool.split(':')
            return [tuple(h.split('\t')) for h in knn.select(n, int(k), int(topn))]
        if a.pool.startswith('tier'):
            # kNN hints at the full boost, then the rest of the original's pool at a weaker factor F
            _, k, topn, f = a.pool.split(':')
            near = [tuple(h.split('\t')) for h in knn.select(n, int(k), int(topn))]
            seen = set(near)
            return near + [(l, r, f) for l, r in pools.get(self.pool_key(n), []) if (l, r) not in seen][:a.max_hints]
        return pools.get(self.pool_key(n), [])[:a.max_hints]

    def round(self, rnd):
        a = self.a
        todo = [n for n in self.names if n not in self.solved]
        if a.online:
            # earlier goals of each original first: their proofs feed the later ones in the same round
            todo.sort(key=lambda n: (int(n.rsplit('__goal_', 1)[1]) if '__goal_' in n else 0, n))
        pools = {}
        knn = None
        hinted = rnd > 0 or (a.hints_extra and a.hints_from_start)
        if hinted:
            if a.pool.startswith(('knn', 'tier')):
                import hintsel
                knn = hintsel.KNN(os.path.join(self.dir, 'hints'), list(self.solved))
                for d in (a.hints_extra.split(',') if a.hints_extra else []):
                    for f in os.listdir(d):
                        if f not in knn.hints:
                            L = [l.rstrip('\n') for l in open(os.path.join(d, f)) if '\t' in l]
                            if L:
                                knn.add(f, L)
            if not a.pool.startswith('knn'):
                pools = self.build_pools()
                if a.online:
                    cnt = collections.defaultdict(collections.Counter)
                    for n in self.solved:
                        for h in self.hints_of(n):
                            cnt[self.pool_key(n)][h] += 1
        if a.model and (rnd > 0 or a.given_extra or a.model_fixed):
            self.train_model(rnd)
        if a.lemmas or a.lemma_knn:
            import lemmas
            self.lemma_src = lemmas.by_original(self.solved)  # proven before this round
            if a.lemma_knn:
                self.lemma_index = lemmas.LemmaIndex(sorted(self.solved), subsets=a.lemma_subsets)
        rdir = os.path.join(self.dir, 'r%d' % rnd)
        os.makedirs(rdir, exist_ok=True)
        t0 = time.time(); new = 0
        with open(os.path.join(rdir, 'results.tsv'), 'w') as rf, \
             open(os.path.join(self.dir, 'solved.tsv'), 'a') as sf, \
             ThreadPoolExecutor(a.j) as ex:
            knn_new = []   # online: proofs not yet in the kNN index (it is rebuilt in batches)
            knn_t = [time.time()]
            streak = collections.Counter()   # --give-up: consecutive failures per original (in completion order)
            def jobs():
                for n in todo:
                    if a.give_up and streak[orig_of(n)] >= a.give_up:
                        continue
                    if a.online and knn is not None and knn_new and (len(knn_new) >= 50 or time.time() - knn_t[0] > 120):
                        for m, L in knn_new:
                            knn.add(m, L)
                        knn_new.clear(); knn_t[0] = time.time()
                    hints = self.hints_for(n, pools, knn) if hinted else []
                    if rnd > 0 and not hints and not a.rerun_unhinted:
                        continue
                    yield n, hints
            def results():
                # at most 4*j runs queued, so results are written as they come
                pending = set(); it = jobs()
                while True:
                    while len(pending) < (a.j if a.online else 4 * a.j):
                        nxt = next(it, None)
                        if nxt is None:
                            break
                        pending.add(ex.submit(self.run_one, nxt[0], nxt[1], rnd))
                    if not pending:
                        return
                    done, pending = wait(pending, return_when=FIRST_COMPLETED)
                    for f in done:
                        yield f.result()
            futs = []
            for k, r in enumerate(results()):
                futs.append(None)
                n, ok, dt, stats, hs = r
                rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{stats}\n'); rf.flush()
                streak[orig_of(n)] = 0 if ok else streak[orig_of(n)] + 1
                if ok:
                    new += 1
                    self.solved[n] = (rnd, dt)
                    sf.write(f'{n}\t{rnd}\t{dt:.2f}\n'); sf.flush()
                    with open(os.path.join(self.dir, 'hints', n), 'w') as hf:
                        for l, r in hs:
                            hf.write(f'{l}\t{r}\n')
                    if a.online and hinted:
                        # the new proof joins the pools for the runs not yet started
                        if knn is not None and hs:
                            knn_new.append((n, [f'{l}\t{r}' for l, r in hs]))
                        if not a.pool.startswith('knn'):
                            key = self.pool_key(n)
                            cnt[key].update(hs)
                            pools[key] = [h for h, _ in cnt[key].most_common()]
                        if getattr(self, 'lemma_src', None) is not None and '__goal_' in n:
                            o, k = lemmas.split(n)
                            self.lemma_src[o] = self.lemma_src.get(o, set()) | {k}  # copy: workers read it
                if (k + 1) % 200 == 0:
                    print(f'  round {rnd}: {k+1}/{len(todo)} new={new} {time.time()-t0:.0f}s',
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
    ap.add_argument('--resume', action='store_true',
                    help='checkpointed loop: unsolved runs dump their state and the next round resumes it with the new hints')
    ap.add_argument('-j', type=int, default=20)
    ap.add_argument('--twee', default='/project/bin/twee')
    ap.add_argument('--args', default='--no-flatten-goal')
    ap.add_argument('--pool', default='original')
    ap.add_argument('--max-hints', type=int, default=100000)
    ap.add_argument('--aux', action='store_true')
    ap.add_argument('--rerun-unhinted', action='store_true')
    ap.add_argument('--lemmas', type=int, default=0,
                    help='rounds > 0: add up to N proven sibling goals (nearest below) as axioms')
    ap.add_argument('--lemma-knn', type=int, default=0,
                    help='rounds > 0: also add up to K proven goals with the same axioms (any original) most similar to the goal')
    ap.add_argument('--model-theory', action='store_true',
                    help='rule model with the ENIGMA theory block (rulemodel.py --theory; e.g. models/rm4t)')
    ap.add_argument('--lemma-subsets', action='store_true',
                    help='--lemma-knn may also use problems whose axioms are a subset of the target\'s')
    ap.add_argument('--online', action='store_true',
                    help='each proof joins the pools (and the sibling lemmas) at once, for the runs not yet started; '
                         'goals run in goal-number order and only -j runs are queued')
    ap.add_argument('--give-up', type=int, default=0,
                    help='skip the rest of an original in this round after N consecutive failures (with --online: goal order)')
    ap.add_argument('--keep-out', action='store_true', help='save each run\'s output in DIR/rN/out/<name> (for stallsim.py)')
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
