#!/usr/bin/env python3
"""Veroff-style hint loop for twee on AIM60k.

Round 0 runs every problem of the set without hints (unless --init DIR
imports an earlier loop's state). Each later round runs every unsolved
problem with a pool of hints taken from the proofs found so far, and adds
the proofs it finds to the pool.

usage: loop.py SET DIR [--rounds N] [--timeout S] [-j N] [--twee BIN]
               [--args "..."] [--pool original|all] [--aux]
"""
import argparse, collections, json, os, random, re, subprocess, sys, time
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
        if a.p9loop:
            os.makedirs(os.path.join(self.dir, 'p9lem'), exist_ok=True)
        import threading
        self.p9_lock = threading.Lock()
        self.model = None  # (model, vocab, goaldir) of the current round
        self.names = [l.strip() for l in open(a.set) if l.strip()]
        self.sig = {}
        self.solved = {}   # name -> (round, time)
        sp = os.path.join(self.dir, 'solved.tsv')
        if os.path.exists(sp):
            for l in open(sp):
                n, r, t = l.split('\t')[:3]
                self.solved[n] = (int(r), float(t))

    def p9_lemmas(self, name):
        """--p9loop: the hint matchers of this goal's earlier failed runs (TPTP formulas, in
        the order they were derived; the latest run's last)."""
        p = os.path.join(self.dir, 'p9lem', name)
        if not os.path.exists(p):
            return []
        seen, out = set(), []   # (parallel --p9-parallel runs may append the same matcher)
        for l in open(p):
            l = l.rstrip('\n')
            if l not in seen:
                seen.add(l); out.append(l)
        return out

    def p9_collect(self, name, out, path):
        """--p9loop (Veroff's P9loop): keep the hint matchers that a failed run derived, as
        lemmas for this goal's later runs. Matchers are consequences of the problem's axioms
        (and of the lemmas given to the run), so they are sound lemmas for the same problem;
        any with a symbol that is not in the problem (a skolem of a conditional goal) is dropped."""
        syms = set(re.findall(r'\b([a-z][A-Za-z0-9_]*)\s*\(', open(path).read())) | \
            set(re.findall(r'\b([a-z][A-Za-z0-9_]*)\b', open(path).read()))
        old = self.p9_lemmas(name)
        seen = set(old)
        new = []
        for line in out.splitlines():
            if not line.startswith('HINTMATCHER '):
                continue
            m = re.match(r'HINTMATCHER \d+ fof\(lemma, axiom, (.*)\)\.\s*$', line)
            if not m:
                continue
            f = m.group(1)
            if f in seen or not set(re.findall(r'\b([a-z][A-Za-z0-9_]*)\b', f)) <= syms:
                continue
            seen.add(f); new.append(f)
        if new:
            with self.p9_lock, open(os.path.join(self.dir, 'p9lem', name), 'a') as fh:
                fh.writelines(f + '\n' for f in new)
        return len(new)

    def p9_attempt(self, name, rnd):
        if not self.a.cascade:
            return rnd - self.a.start
        p = os.path.join(self.dir, 'p9lem', name + '.attempts')
        return int(open(p).read()) if os.path.exists(p) else 0

    def p9_precedence(self, path, k):
        """Ordering k > 0: a fixed pseudo-random permutation of the problem's function symbols."""
        syms = set()
        for line in open(path):
            m = re.match(r'\s*(?:cnf|fof)\(\s*[^,]+,\s*[^,]+,(.*)', line)
            if m:
                syms |= set(re.findall(r'\b([a-z][A-Za-z0-9_]*)\b', m.group(1)))
        syms = sorted(syms)
        random.Random(1000003 * k + 17).shuffle(syms)
        return syms

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
        self.pool_cnt_u = collections.defaultdict(collections.Counter)
        for n in self.solved:
            key = self.pool_key(n)
            hs = self.hints_of(n)
            for h in hs:
                cnt[key][h] += 1
            self.count_uncond(n, hs)
        self.pool_cnt = cnt
        return {k: [h for h, _ in c.most_common()] for k, c in cnt.items()}

    def count_uncond(self, n, hs):
        """Pool counts from proofs of unconditional goals only (--hint-axioms): a conditional
        goal's hypotheses have skolems that hint generalisation turns into variables, so
        their proofs can carry false 'hints' such as X0 = X1 (runs before twee-e14)."""
        if not self.a.hint_axioms or '__goal_' not in n:
            return
        import lemmas
        f = lemmas.conjecture(n)
        if f and lemmas.unit_eq(f):
            self.pool_cnt_u[self.pool_key(n)].update((l, r) for l, r, *_ in hs)

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
          here = os.path.dirname(os.path.abspath(__file__))
          subprocess.run([VENV_PY, os.path.join(here, 'rulemodel.py'),
                        ','.join(dirs), '--all', '--ntest', '0', '--save', m, '--vocab', v,
                        '--negmax', str(a.model_negmax), '--threads', str(a.model_threads)
                       ] + (['--theory'] if a.model_theory else []),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env=dict(os.environ, OMP_NUM_THREADS=str(a.model_threads)))
          # binary forest: loads in 0.07 s instead of 0.25 s
          mb = m[:-4] + '.bin'
          subprocess.run([VENV_PY, os.path.join(here, 'lgb2bin.py'), m, mb],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
          if os.path.exists(mb):
              m = mb
        import rulemodel
        rulemodel.THEORY = a.model_theory
        vocab = {}
        for line in open(v):
            c, k = line.rstrip('\n').split('\t'); vocab[k] = int(c)
        gdir = os.path.join(self.dir, 'goals', 'r%d' % rnd); os.makedirs(gdir, exist_ok=True)
        for n in self.names:
            if n not in self.solved or a.rerun_solved:
                rulemodel.write_goalfile(n, vocab, os.path.join(gdir, n))
        self.model = (m, v, gdir)
        print(f'  round {rnd}: trained rule model {time.time()-t0:.0f}s', file=sys.stderr, flush=True)

    def run_one(self, name, hints, rnd, budget=None, resume=None, max_cpu=None, variant=0):
        """One twee run. BUDGET (default: the round's timeout), RESUME (default --resume)
        and MAX_CPU (replaces --max-cpu in --args) are for --cascade. VARIANT: which of the
        --p9-parallel runs of this goal in this round (Bigloop)."""
        a = self.a
        tag = name + (f'.v{variant}' if variant else '')   # tmp file names
        T = budget if budget is not None else self.timeout(rnd)
        resume = a.resume if resume is None else resume
        path = os.path.join(PROB, name + '.p')
        if (a.lemmas or a.lemma_knn) and rnd > 0 and self.lemma_src:
            import lemmas
            if a.lemma_knn:
                txt, nl = lemmas.lemma_problem_knn(name, self.lemma_src, a.lemmas, self.lemma_index, a.lemma_knn, a.lemma_after)
            else:
                txt, nl = lemmas.lemma_problem(name, self.lemma_src, a.lemmas, a.lemma_after)
            if nl:
                path = os.path.join(self.dir, 'tmp', tag + '.p')
                with open(path, 'w') as f:
                    f.write(txt)
        if a.hint_axioms and rnd > 0:
            # the K most frequent pool hints that come from at least F sibling proofs, as axioms
            # (pool hints are skolem-free consequences of the axioms and proven lemmas: sound)
            k, fmin = (int(x) for x in a.hint_axioms.split(':'))
            cnt = self.pool_cnt_u.get(self.pool_key(name), collections.Counter())
            ax = [h for h, c in cnt.most_common() if c >= fmin][:k]
            if ax:
                txt = open(path).read().rstrip('\n') + '\n' + ''.join(
                    f'cnf(hint_axiom_{i}, axiom, {l} = {r}).\n' for i, (l, r) in enumerate(ax))
                path = os.path.join(self.dir, 'tmp', tag + '.p')
                with open(path, 'w') as f:
                    f.write(txt)
        orig_path = os.path.join(PROB, name + '.p')
        p9 = self.p9_lemmas(name) if a.p9loop else []
        if a.p9_max and len(p9) > a.p9_max:
            p9 = p9[-a.p9_max:]   # the most recently derived
        if p9:
            txt = open(path).read().rstrip('\n') + '\n' + ''.join(
                f'fof(p9lemma_{i}, axiom, {f}).\n' for i, f in enumerate(p9))
            path = os.path.join(self.dir, 'tmp', tag + '.p')
            with open(path, 'w') as f:
                f.write(txt)
        args = a.args.split()
        if max_cpu is not None:
            args = [x for i, x in enumerate(args) if x != '--max-cpu' and (i == 0 or args[i - 1] != '--max-cpu')]
            args += ['--max-cpu', str(max_cpu)]
        cmd = [a.twee, path, '--max-time', str(T), '--no-colour', '--quiet',
               '--no-proof', '--print-hints', '--print-given'] + args
        if a.p9loop:
            cmd += ['--print-hint-matchers']
        k = 0
        if a.p9_orders > 1:
            # P9loop's term orderings: attempt k of a goal (rounds from --start, or the number of
            # its earlier p9 attempts) uses ordering k mod N; ordering 0 is twee's default
            # (Bigloop, --p9-parallel P: the P runs of a round take orderings attempt*P .. attempt*P+P-1)
            k = (self.p9_attempt(name, rnd) * max(1, a.p9_parallel) + variant) % a.p9_orders
            if k:
                cmd += ['--precedence', ','.join(self.p9_precedence(orig_path, k))]
        if self.model:
            m, v, gdir = self.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, name)] + \
                   a.model_args.split()
        if hints and a.stall:
            cmd += ['--eqhint-stall', str(a.stall)]
        spath = os.path.join(self.dir, 'states', name + '.bin')
        if resume:   # True: continue the saved state; 'fresh': start over but save (replaces the old state)
            if resume != 'fresh' and os.path.exists(spath):
                cmd += ['--load-state', spath]
            cmd += ['--dump-state', spath + '.tmp']
        if hints:
            hpath = os.path.join(self.dir, 'tmp', tag + '.hints')
            with open(hpath, 'w') as f:
                for h in hints:
                    f.write('\t'.join(h) + '\n')
            cmd += ['--hints-file', hpath]
        if os.environ.get('LOOP_PRINT_CMD'):
            print('CMD', ' '.join(cmd), file=sys.stderr, flush=True)
        t0 = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=T * (a.wall_factor if "--abstract-time" in self.a.args else 1) + 30)
            out = p.stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b'').decode('utf8', 'replace') + '\nKILLED\n'
        dt = time.time() - t0
        if a.keep_out:
            od = os.path.join(self.dir, 'r%d' % rnd, 'out'); os.makedirs(od, exist_ok=True)
            i, j = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
            with open(os.path.join(od, tag), 'w') as f:
                f.write(out[:i] + out[j:] if 0 <= i < j else out)  # without the given rules
        if hints and not os.environ.get('LOOP_KEEP_TMP'):
            os.unlink(hpath)
        ok = 'HINTS-END' in out
        if a.p9loop and not ok:
            nnew = self.p9_collect(name, out, orig_path)
            out += f'\nP9LEMMAS used={len(p9)} new={nnew}\n'
        if a.p9loop and a.cascade:   # the goal's attempt count (its next ordering)
            with self.p9_lock:
                ap = os.path.join(self.dir, 'p9lem', name + '.attempts')
                n0 = int(open(ap).read()) if os.path.exists(ap) else 0
                with open(ap, 'w') as fh:
                    fh.write(str(n0 + 1))
        if resume:
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
        if a.p9loop:
            stats += f' P9 used={len(p9)}' + (f' new={nnew}' if not ok else '') + \
                (f' v={variant} ord={k}' if a.p9_orders > 1 else '')
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
            gp = os.path.join(self.dir, 'given', name)
            npos = sum(1 for x in rows if x[0] == '1')
            old = -1
            if os.path.exists(gp):   # solved before (--rerun-solved): keep the shorter proof's log
                old = sum(1 for x in open(gp) if x[0] == '1')
            if old < 0 or npos < old:
                with open(gp, 'w') as gf:
                    gf.writelines(rows)
            res = hs
        if path.startswith(os.path.join(self.dir, 'tmp')) and not os.environ.get('LOOP_KEEP_TMP'):
            os.unlink(path)
        return name, ok, dt, stats, res

    def run_multi(self, names, hints, rnd):
        """--multi: one twee --multi-goal run for a window of unconditional goals of one
        original, with the union of their lemmas and the budget of all of them. Returns one
        result per goal; the window's hints go with its first proved goal."""
        a = self.a
        import lemmas
        lines = [l for l in open(os.path.join(PROB, names[0] + '.p'))
                 if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l]
        lem = {}
        if (a.lemmas or a.lemma_knn) and rnd > 0 and self.lemma_src:
            for n in names:
                if a.lemma_knn:
                    txt, _ = lemmas.lemma_problem_knn(n, self.lemma_src, a.lemmas, self.lemma_index, a.lemma_knn, a.lemma_after)
                else:
                    txt, _ = lemmas.lemma_problem(n, self.lemma_src, a.lemmas, a.lemma_after)
                for m in re.finditer(r'^fof\(lemma_\w+,axiom,(.*)\)\.\s*$', txt, re.M):
                    lem.setdefault(m.group(1).strip(), len(lem))
        lines += [f'fof(lemma_{i},axiom,{f}).\n' for f, i in lem.items()]
        lines += [f'cnf({n},negated_conjecture,{lemmas.negated_goal(n, lemmas.split(n)[1])}).\n' for n in names]
        path = os.path.join(self.dir, 'tmp', names[0] + '.multi.p')
        with open(path, 'w') as f:
            f.writelines(lines)
        T = self.timeout(rnd) * len(names)
        args = a.args.split()
        for i in range(len(args) - 1):
            if args[i] == '--max-cpu':
                args[i + 1] = str(float(args[i + 1]) * len(names))
        cmd = [a.twee, path, '--max-time', str(T), '--no-colour', '--quiet', '--no-proof',
               '--print-hints', '--multi-goal'] + args
        if self.model:
            m, v, gdir = self.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, names[0])] + \
                   a.model_args.split()
        if hints:
            hpath = os.path.join(self.dir, 'tmp', names[0] + '.multi.hints')
            with open(hpath, 'w') as f:
                for h in hints:
                    f.write('\t'.join(h) + '\n')
            cmd += ['--hints-file', hpath]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=T * (a.wall_factor if "--abstract-time" in a.args else 1) + 30)
            out = p.stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b'').decode('utf8', 'replace') + '\nKILLED\n'
        dt = time.time() - t0
        if a.keep_out:
            od = os.path.join(self.dir, 'r%d' % rnd, 'out'); os.makedirs(od, exist_ok=True)
            with open(os.path.join(od, names[0] + '.multi'), 'w') as f:
                f.write(f'WINDOW {" ".join(names)}\n' + out)
        if hints:
            os.unlink(hpath)
        os.unlink(path)
        got = {}
        stats = ''
        for line in out.splitlines():
            if line.startswith('SOLVEDGOAL '):
                w = line.split()
                got[w[1]] = w[2]
            elif line.startswith('HINTSTATS'):
                stats = line
        hs = []
        if got and 'HINTS-END' in out:
            L, G = hintlib.extract_hints(out)
            sig = self.signature(names[0])
            seen = set()
            for l, r in L + G:
                k = canon_key(l, r, sig)
                if l == r or k[0] == k[1] or k in seen:
                    continue
                seen.add(k); hs.append(k)
        res, first = [], True
        for n in names:
            if n in got:
                res.append((n, True, dt, f'MULTI {len(names)} {got[n]} {stats}', hs if first else []))
                first = False
            else:
                res.append((n, False, dt, f'MULTI {len(names)} {stats}', None))
        return res

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
        hs = pools.get(self.pool_key(n), [])[:a.max_hints]
        if a.freq_factors:
            # weaker boosts for hints from few sibling proofs (their precision is far lower)
            steps = sorted((int(c), f) for c, f in (x.split(':') for x in a.freq_factors.split(',')))
            cnt = self.pool_cnt[self.pool_key(n)]
            def fac(h):
                c = cnt[h]
                for m, f in steps:
                    if c <= m:
                        return h + (f,)
                return h
            hs = [fac(h) for h in hs]
        return hs

    def cascade(self):
        """--cascade T0,T1,..: frontier deepening instead of rounds (pool original, online).

        A goal is retried at T0 whenever its sibling-lemma context (the nearest proven
        siblings, as lemmas.py picks them) has changed since its last attempt (a sibling
        nearer to it got proved) and it is at most --retry-gap places after a proven
        sibling. Otherwise the frontier is deepened: goals at most
        --frontier places after a proven sibling (in the set's goal order) run at the next
        budget level, resuming the saved state of their previous level (budget T[L] - T[L-1]).
        Deepening jobs leave --reserve workers free for the retries. --cascade-start L: the
        unsolved goals count as tried up to level L in their current context (e.g. 0 after a
        round at T0); -1: untried."""
        import bisect, lemmas
        a = self.a
        rnd = a.start
        T = [float(x) for x in a.cascade.split(',')]
        pools = self.build_pools(); cnt = self.pool_cnt
        if a.model:
            self.train_model(rnd)
        self.lemma_src = {o: set(v) for o, v in lemmas.by_original(self.solved).items()}
        if a.lemma_knn:
            self.lemma_index = lemmas.LemmaIndex(sorted(self.solved), subsets=a.lemma_subsets)
        byo = collections.defaultdict(list)   # the set's goals and the proven goals of their originals
        for n in set(self.names) | set(self.solved):
            if '__goal_' in n:
                byo[orig_of(n)].append(n)
        origs = {orig_of(n) for n in self.names}
        byo = {o: L for o, L in byo.items() if o in origs}
        for o in byo:
            byo[o].sort(key=lambda n: lemmas.split(n)[1])
        srt = {}   # original -> sorted proven goal numbers (dropped when a proof arrives)
        def ctx(n, after=None):
            o, k = lemmas.split(n)
            if o not in srt:
                srt[o] = sorted(self.lemma_src.get(o, ()))
            pr = srt[o]
            i = bisect.bisect_left(pr, k)
            below = pr[max(0, i - a.lemmas):i]
            if not (a.lemma_after if after is None else after):
                return tuple(below)
            # as lemmas.lemma_problem: the a.lemmas nearest proven siblings on either side
            near = sorted(below + pr[i:i + a.lemmas], key=lambda j: (abs(k - j), j))[:a.lemmas]
            return tuple(sorted(near))
        def gaps():
            """unsolved goal -> places after the nearest proven goal below it (in the set)."""
            g = {}
            for o, L in byo.items():
                last = None
                for i, n in enumerate(L):
                    if n in self.solved:
                        last = i
                    else:
                        g[n] = (i - last) if last is not None else 10**6
            return g
        # --cascade-start -1: nothing tried yet, so the goals near a proof all get a T0 run first
        # --cascade-was-below: the earlier attempts had lemmas from below only, so with
        # --lemma-after exactly the goals that now get lemmas from above are retried
        att = {n: ((ctx(n, False if a.cascade_was_below else None), a.cascade_start) if a.cascade_start >= 0
                   else (None, -1))
               for n in self.names if n not in self.solved}
        running = {}   # future -> (name, level)
        rdir = os.path.join(self.dir, 'r%d' % rnd); os.makedirs(rdir, exist_ok=True)
        t0 = time.time(); new = 0; done_n = 0
        with open(os.path.join(rdir, 'results.tsv'), 'a') as rf, \
             open(os.path.join(self.dir, 'solved.tsv'), 'a') as sf, \
             ThreadPoolExecutor(a.j) as ex:
            while True:
                busy = {n for n, _ in running.values()}
                if time.time() - t0 < a.cascade_hours * 3600:
                    g = gaps()
                    retry = sorted((g[n], lemmas.split(n)[1], n) for n in att
                                   if n not in busy and ctx(n) != att[n][0] and g[n] <= a.retry_gap)
                    deep_running = collections.Counter(orig_of(n) for n, l in running.values() if l > 0)
                    deep = sorted((att[n][1] + 1, deep_running[orig_of(n)], g[n], lemmas.split(n)[1], n) for n in att
                                  if n not in busy and ctx(n) == att[n][0] and att[n][1] + 1 < len(T)
                                  and g[n] <= a.frontier)
                    while len(running) < a.j and (retry or deep):
                        if retry:
                            n = retry.pop(0)[-1]; lev = 0
                            att[n] = (ctx(n), 0)
                            # fresh in the new context; its state replaces any older one, so deepening
                            # continues this search
                            # (--p9loop: no states; the goal's matcher lemmas carry over instead)
                            fut = ex.submit(self.run_one, n, self.hints_for(n, pools, None), rnd,
                                            T[0], False if a.p9loop else 'fresh', a.cascade_cpu * T[0])
                        else:
                            if sum(1 for _, l in running.values() if l > 0) >= a.j - a.reserve:
                                break
                            lev, _, _, _, n = deep.pop(0)
                            if any(m == n for m, _ in running.values()):
                                continue
                            att[n] = (ctx(n), lev)
                            sp = os.path.join(self.dir, 'states', n + '.bin')
                            # --p9loop (P9loop deepening): a fresh run of the level's increment, with the
                            # matcher lemmas of the goal's earlier runs and its next ordering, not a resume
                            b = T[lev] - T[lev - 1] if (a.p9loop or os.path.exists(sp)) else T[lev]
                            fut = ex.submit(self.run_one, n, self.hints_for(n, pools, None), rnd,
                                            b, not a.p9loop, a.cascade_cpu * b)
                        running[fut] = (n, lev)
                if not running:
                    break
                fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
                for f in fin:
                    n0, lev = running.pop(f)
                    n, ok, dt, stats, hs = f.result()
                    done_n += 1
                    rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{stats}\tL{lev}\tt={time.time()-t0:.0f}\n'); rf.flush()
                    if ok:
                        new += 1
                        att.pop(n, None)
                        self.solved[n] = (rnd, dt)
                        sf.write(f'{n}\t{rnd}\t{dt:.2f}\n'); sf.flush()
                        with open(os.path.join(self.dir, 'hints', n), 'w') as hf:
                            for l, r in hs:
                                hf.write(f'{l}\t{r}\n')
                        key = self.pool_key(n)
                        cnt[key].update(hs)
                        self.count_uncond(n, hs)
                        pools[key] = [h for h, _ in cnt[key].most_common()]
                        o, k = lemmas.split(n)
                        self.lemma_src[o] = self.lemma_src.get(o, set()) | {k}
                        srt.pop(o, None)
                    if done_n % 50 == 0:
                        print(f'  cascade: {done_n} runs, new={new}, {len(running)} running, '
                              f'{time.time()-t0:.0f}s', file=sys.stderr, flush=True)
        msg = f'cascade: {done_n} runs new {new} total {len(self.solved)}/{len(self.names)} {time.time()-t0:.0f}s'
        print(msg, file=sys.stderr, flush=True)
        with open(os.path.join(self.dir, 'log.txt'), 'a') as lf:
            lf.write(msg + '\n')
        return new

    def round(self, rnd):
        a = self.a
        todo = [n for n in self.names if n not in self.solved or (a.rerun_solved and rnd > 0)]
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
                cnt = self.pool_cnt   # updated online
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
            units = [[n] for n in todo]
            if a.multi > 1:
                # windows of up to MULTI consecutive unconditional goals of one original (goal order)
                import lemmas
                units, cur = [], {}
                for n in todo:
                    if '__goal_' not in n or lemmas.negated_goal(n, 0) is None:
                        units.append([n]); continue
                    o = orig_of(n)
                    if o not in cur or len(cur[o]) >= a.multi:
                        cur[o] = []; units.append(cur[o])
                    cur[o].append(n)
            def jobs():
                for u in units:
                    n = u[0]
                    if a.give_up and streak[orig_of(n)] >= a.give_up:
                        continue
                    if a.online and knn is not None and knn_new and (len(knn_new) >= 50 or time.time() - knn_t[0] > 120):
                        for m, L in knn_new:
                            knn.add(m, L)
                        knn_new.clear(); knn_t[0] = time.time()
                    hints = self.hints_for(n, pools, knn) if hinted else []
                    if rnd > 0 and not hints and not a.rerun_unhinted:
                        continue
                    yield u, hints
            def results():
                # at most 4*j runs queued, so results are written as they come
                pending = set(); it = jobs()
                while True:
                    while len(pending) < (a.j if a.online else 4 * a.j):
                        nxt = next(it, None)
                        if nxt is None:
                            break
                        u = nxt[0]
                        if len(u) > 1:
                            pending.add(ex.submit(self.run_multi, u, nxt[1], rnd))
                        else:
                            for v in range(max(1, a.p9_parallel)):   # Bigloop: P runs of the goal at once
                                pending.add(ex.submit(lambda n=u[0], h=nxt[1], v=v: [self.run_one(n, h, rnd, variant=v)]))
                    if not pending:
                        return
                    done, pending = wait(pending, return_when=FIRST_COMPLETED)
                    for f in done:
                        yield from f.result()
            futs = []
            for k, r in enumerate(results()):
                futs.append(None)
                n, ok, dt, stats, hs = r
                rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{stats}\tt={time.time()-t0:.0f}\n'); rf.flush()
                streak[orig_of(n)] = 0 if ok else streak[orig_of(n)] + 1
                if ok and n in self.solved:
                    # --rerun-solved: solved again; keep the shorter proof's hints
                    hp = os.path.join(self.dir, 'hints', n)
                    if not os.path.exists(hp) or len(hs) < sum(1 for _ in open(hp)):
                        with open(hp, 'w') as hf:
                            for l, r in hs:
                                hf.write(f'{l}\t{r}\n')
                elif ok:
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
                            self.count_uncond(n, hs)
                            pools[key] = [h for h, _ in cnt[key].most_common()]
                        if getattr(self, 'lemma_src', None) is not None and '__goal_' in n:
                            o, gk = lemmas.split(n)
                            self.lemma_src[o] = self.lemma_src.get(o, set()) | {gk}  # copy: workers read it
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
    ap.add_argument('--model-negmax', type=int, default=400, help='negative rules per problem when training (memory)')
    ap.add_argument('--model-threads', type=int, default=8)
    ap.add_argument('--rerun-solved', action='store_true',
                    help='ENIGMA-style loop: rounds > 0 rerun the solved problems too; the shorter proof\'s given log '
                         'and hints are kept, so the next model trains on new and shorter proofs')
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
    ap.add_argument('--lemma-after', action='store_true',
                    help='sibling lemmas are the nearest proven goals above N as well as below (all proven '
                         'before the run, so still well-founded)')
    ap.add_argument('--hint-axioms', default='',
                    help='K:F: also add the K most frequent pool hints that occur in >= F sibling proofs as axioms')
    ap.add_argument('--lemma-subsets', action='store_true',
                    help='--lemma-knn may also use problems whose axioms are a subset of the target\'s')
    ap.add_argument('--online', action='store_true',
                    help='each proof joins the pools (and the sibling lemmas) at once, for the runs not yet started; '
                         'goals run in goal-number order and only -j runs are queued')
    ap.add_argument('--freq-factors', default='',
                    help='pool hints by frequency: "1:0.2,4:0.05" gives hints from 1 sibling proof factor 0.2, '
                         'from 2-4 factor 0.05, the rest the default (--eqhint-factor, 0.01)')
    ap.add_argument('--wall-factor', type=float, default=5,
                    help='with --abstract-time: kill a run after FACTOR * timeout + 30 wall seconds')
    ap.add_argument('--multi', type=int, default=0,
                    help='windows of up to N consecutive unconditional goals of one original run as one '
                         'twee --multi-goal search, with all their lemmas and N times the budget')
    ap.add_argument('--cascade', default='',
                    help='T0,T1,...: frontier deepening instead of rounds (see Loop.cascade), from round --start')
    ap.add_argument('--cascade-start', type=int, default=0,
                    help='--cascade: unsolved goals count as tried up to this level in their current context')
    ap.add_argument('--cascade-was-below', action='store_true',
                    help='--cascade with --lemma-after: earlier attempts used lemmas from below only')
    ap.add_argument('--cascade-hours', type=float, default=1e9, help='--cascade: no new runs after this many hours')
    ap.add_argument('--cascade-cpu', type=float, default=10, help='--cascade: --max-cpu per abstract second of budget')
    ap.add_argument('--retry-gap', type=int, default=6,
                    help='--cascade: retry a goal with a changed context only if at most this many places after a proven sibling')
    ap.add_argument('--frontier', type=int, default=1,
                    help='--cascade: deepen goals at most this many places after a proven sibling')
    ap.add_argument('--reserve', type=int, default=3, help='--cascade: workers kept free of deepening runs')
    ap.add_argument('--give-up', type=int, default=0,
                    help='skip the rest of an original in this round after N consecutive failures (with --online: goal order)')
    ap.add_argument('--keep-out', action='store_true', help='save each run\'s output in DIR/rN/out/<name> (for stallsim.py)')
    ap.add_argument('--p9loop', action='store_true',
                    help="Veroff's P9loop: the hint matchers of a goal's failed runs become lemmas (axioms) of its later runs")
    ap.add_argument('--p9-orders', type=int, default=1,
                    help='--p9loop: cycle through this many term orderings (KBO precedences) over a goal\'s attempts')
    ap.add_argument('--p9-parallel', type=int, default=1,
                    help='Veroff\'s Bigloop: P runs of each goal per round at once, each with its own ordering '
                         '(needs --p9-orders >= P), sharing one lemma pool (their matchers join it after the round\'s runs)')
    ap.add_argument('--p9-max', type=int, default=0, help='--p9loop: at most this many lemmas, the most recently derived (0 = all)')
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
    if a.cascade:
        lp.cascade()
        return
    for r in range(a.start, a.start + a.rounds):
        if lp.round(r) == 0 and r > 0 and not a.p9loop and not a.resume:
            break   # (--p9loop and --resume runs change between rounds even without new proofs)

if __name__ == '__main__':
    main()
