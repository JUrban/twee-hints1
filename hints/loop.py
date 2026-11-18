#!/usr/bin/env python3
"""Veroff-style hint loop for twee on AIM60k.

Round 0 runs every problem of the set without hints (unless --init DIR
imports an earlier loop's state). Each later round runs every unsolved
problem with a pool of hints taken from the proofs found so far, and adds
the proofs it finds to the pool.

usage: loop.py SET DIR [--rounds N] [--timeout S] [-j N] [--twee BIN]
               [--args "..."] [--pool original|all] [--aux]
"""
import argparse, collections, heapq, json, math, os, random, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib
import given as givenlib

VENV_PY = '/project/hintwork/venv/bin/python'

PROB = hintlib.PROB
HERE = os.path.dirname(os.path.abspath(__file__))

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
        self.gen_lock = threading.Lock(); self.gen_stats = [0, 0, 0.0]   # --gen-model: calls, hints, seconds
        self.p9_uncond = {}
        self.model = None  # (model, vocab, goaldir) of the current round
        self.names = [l.strip() for l in open(a.set) if l.strip()]
        self.sig = {}
        self.solved = {}   # name -> (round, time)
        sp = os.path.join(self.dir, 'solved.tsv')
        self.solved_off = 0   # (--sync reads the rows appended after this offset)
        if os.path.exists(sp):
            with open(sp) as f:
                for l in f.readlines():
                    if not l.endswith('\n'):
                        break
                    self.solved_off += len(l.encode())
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

    def gen_save(self, name, out, path):
        """--gen-model: the axiom rows and the last --gen-ctx rules of a failed run, in the given
        log format (all labelled 0), for the hints of its next (resumed) level."""
        sig = self.signature(name)
        ax = set(givenlib.key(l, r, sig) for l, r in givenlib.axioms(name, path))
        A, R = [], []
        for idx, x in enumerate(givenlib.parse_given_parents(out)):
            if x is None or x[0] == x[1]:
                continue
            k = givenlib.key(x[0], x[1], sig)
            (A if k in ax else R).append(f'{-1 if k in ax else 0}\t{idx}\t{k[0]}\t{k[1]}\n')
        if not R:
            return
        d = os.path.join(self.dir, 'genctx'); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name + '.tmp'), 'w') as f:
            f.writelines(A + R[-self.a.gen_ctx:])
        os.replace(os.path.join(d, name + '.tmp'), os.path.join(d, name))

    def gen_hints(self, name, hints):
        """--gen-model (15 Nov, gen.py): HINTS plus --gen-n equations sampled by the hint
        generator from the goal and the saved context of its previous level."""
        a = self.a
        cp = os.path.join(self.dir, 'genctx', name)
        if not os.path.exists(cp):
            return hints
        cmd = [a.gen_python, os.path.join(HERE, a.gen_script), 'hints', cp, name, '--load', a.gen_model,
               '--n', str(a.gen_n), '--threads', '1', '--ctx', str(a.gen_ctx), '--temp', str(a.gen_temp)]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=120)
        except subprocess.TimeoutExpired:
            return hints
        have = {tuple(h[:2]) for h in hints}
        gen = [tuple(l.split('\t')[:2]) for l in p.stdout.decode().splitlines() if l.count('\t') == 1]
        gen = [g for g in gen if g not in have and (g[1], g[0]) not in have]
        with self.gen_lock:
            self.gen_stats[0] += 1; self.gen_stats[1] += len(gen); self.gen_stats[2] += time.time() - t0
            if self.gen_stats[0] % 20 == 1:
                c, h, sec = self.gen_stats
                print(f'  --gen-model: {c} calls, {h / c:.0f} new hints and {sec / c:.1f}s per call', flush=True)
        return list(hints) + gen

    def gen_cuts_problem(self, name, path, tag, hints):
        """--gen-cuts K (15 Nov; Chvalovsky-Suda-Urban IWIL 2026: generated lemmas as cuts, accepted
        when the prover proves them): the generator samples --gen-n equations from the goal and the
        saved context of its previous level; the K most often sampled (not variants of the goal) go
        as negated conjectures into one twee --multi-goal run of --gen-cut-time abstract s on the
        goal's axioms and lemmas; those proved after at least --gen-cut-min considered critical
        pairs are added to the goal's problem as axioms. Returns the problem's path."""
        a = self.a
        cp = os.path.join(self.dir, 'genctx', name)
        if not os.path.exists(cp):
            return path
        t0 = time.time()
        cmd = [a.gen_python, os.path.join(HERE, a.gen_script), 'hints', cp, name, '--load', a.gen_model,
               '--n', str(a.gen_n), '--threads', '1', '--ctx', str(a.gen_ctx), '--temp', str(a.gen_temp), '--counts', '1']
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=300)
        except subprocess.TimeoutExpired:
            return path
        def canon(l, r):   # variant key, both orientations
            def key(x):
                ren = {}
                return re.sub(r'\bX\d+\b', lambda m: ren.setdefault(m.group(0), f'V{len(ren)}'), x)
            return min(key(l + '=' + r), key(r + '=' + l))
        import hintsel
        try:
            goal = {canon(l, r) for _, l, r in hintsel.goal_lits(name)}
        except Exception:
            goal = set()
        cands = []
        for line in p.stdout.decode().splitlines():
            w = line.split('\t')
            if len(w) >= 2 and canon(w[0], w[1]) not in goal:
                cands.append((w[0], w[1]))
            if len(cands) >= a.gen_cuts:
                break
        if not cands:
            return path
        base = [l for l in open(path) if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l]
        if a.gen_cut_sep:
            proved = self.prove_cuts_sep(name, base, cands, tag, hints)
            return self.add_cuts(name, path, tag, cands, proved, t0)
        neg = []
        for i, (l, r) in enumerate(cands):
            sk = lambda s, i=i: re.sub(r'\bX(\d+)\b', lambda m: f'sk_c{i}_{m.group(1)}', s)
            neg.append(f'cnf(cand_{i},negated_conjecture,{sk(l)} != {sk(r)}).\n')
        mpath = os.path.join(self.dir, 'tmp', tag + '.cuts.p')
        with open(mpath, 'w') as f:
            f.writelines(base + neg)
        mcmd = [a.twee, mpath, '--max-time', str(a.gen_cut_time), '--no-colour', '--quiet', '--no-proof',
                '--multi-goal'] + [x for x in a.args.split()]
        if hints:
            hpath = os.path.join(self.dir, 'tmp', tag + '.cuts.hints')
            with open(hpath, 'w') as f:
                for h in hints:
                    f.write('\t'.join(h) + '\n')
            mcmd += ['--hints-file', hpath]
        if self.model:
            m, v, gdir = self.model
            mcmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, name)] + a.model_args.split()
        try:
            q = subprocess.run(mcmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=a.gen_cut_time * (a.wall_factor if '--abstract-time' in a.args else 1) + 30)
            out = q.stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b'').decode('utf8', 'replace')
        if not os.environ.get('LOOP_KEEP_TMP'):
            for x in (mpath, os.path.join(self.dir, 'tmp', tag + '.cuts.hints')):
                if os.path.exists(x):
                    os.unlink(x)
        proved = []
        for line in out.splitlines():
            if line.startswith('SOLVEDGOAL cand_'):
                w = line.split()
                i = int(w[1][5:]); c = int(w[2].split('=')[1])
                if c >= a.gen_cut_min:
                    proved.append(i)
        return self.add_cuts(name, path, tag, cands, proved, t0)

    def prove_cuts_sep(self, name, base, cands, tag, hints):
        """--gen-cut-sep: each cut in its own run of --gen-cut-time, with the kNN lemmas of its own
        statement (in place of the goal's) and the rule model's goal block of the cut: twee's
        completion barely depends on the goal, so a cut proved in a shared run of the goal's own
        problem is mostly already in the goal's state (oracle test, 15 Nov); goal-relative
        guidance is what can make a cut's search differ."""
        a = self.a
        import lemmas
        keep = [l for l in base if not l.startswith('fof(lemma_knn_')]
        hpath = None
        if hints:
            hpath = os.path.join(self.dir, 'tmp', tag + '.cuts.hints')
            with open(hpath, 'w') as f:
                for h in hints:
                    f.write('\t'.join(h) + '\n')
        proved = []
        for i, (l, r) in enumerate(cands):
            txt = list(keep)
            if a.lemma_knn and getattr(self, 'lemma_index', None) is not None:
                o = orig_of(name)
                have = set(re.findall(r'fof\(lemma_goal_(\d+),', ''.join(keep)))
                for j, x in enumerate(self.lemma_index.select(name, a.lemma_knn, exclude={f'{o}__goal_{g}' for g in have},
                                                              eq=(l, r))):
                    txt.append(f'fof(lemma_knn_{j}_{x},axiom,{lemmas.lemma_form(x)}).\n')
            sk = lambda s: re.sub(r'\bX(\d+)\b', lambda m: f'sk_c_{m.group(1)}', s)
            txt.append(f'cnf(cand_{i},negated_conjecture,{sk(l)} != {sk(r)}).\n')
            mpath = os.path.join(self.dir, 'tmp', f'{tag}.cut{i}.p')
            with open(mpath, 'w') as f:
                f.writelines(txt)
            mcmd = [a.twee, mpath, '--max-time', str(a.gen_cut_time), '--no-colour', '--quiet', '--no-proof',
                    '--multi-goal'] + a.args.split()
            if hpath:
                mcmd += ['--hints-file', hpath]
            if self.model:
                m, v, gdir = self.model
                import rulemodel
                vocab = getattr(self, '_rm_vocab', None)
                if vocab is None:
                    vocab = self._rm_vocab = {k: int(c) for c, k in (x.rstrip('\n').split('\t') for x in open(v))}
                gpath = mpath + '.goal'
                rulemodel.write_goalfile(name, vocab, gpath, lits=[(True, l, r)])
                mcmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', gpath] + a.model_args.split()
            try:
                q = subprocess.run(mcmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   timeout=a.gen_cut_time * (a.wall_factor if '--abstract-time' in a.args else 1) + 30)
                out = q.stdout.decode('utf8', 'replace')
            except subprocess.TimeoutExpired as e:
                out = (e.stdout or b'').decode('utf8', 'replace')
            for line in out.splitlines():
                if line.startswith('SOLVEDGOAL cand_') and int(line.split()[2].split('=')[1]) >= a.gen_cut_min:
                    proved.append(i)
            if not os.environ.get('LOOP_KEEP_TMP'):
                for x in (mpath, mpath + '.goal'):
                    if os.path.exists(x):
                        os.unlink(x)
        if hpath and not os.environ.get('LOOP_KEEP_TMP'):
            os.unlink(hpath)
        return proved

    def add_cuts(self, name, path, tag, cands, proved, t0):
        a = self.a
        with self.gen_lock:
            st = self.gen_stats; st[0] += 1; st[1] += len(proved); st[2] += time.time() - t0
            if st[0] % 10 == 1:
                print(f'  --gen-cuts: {st[0]} goals, {st[1] / st[0]:.1f} cuts proved of {a.gen_cuts} per goal, '
                      f'{st[2] / st[0]:.1f}s per goal', flush=True)
        d = os.path.join(self.dir, 'cuts'); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name), 'a') as f:
            f.write(''.join(f'{cands[i][0]}\t{cands[i][1]}\n' for i in proved) + '--\n')
        if not proved:
            return path
        cpath = os.path.join(self.dir, 'tmp', tag + '.cut.p')
        with open(cpath, 'w') as f:
            f.writelines(open(path).readlines() + [f'cnf(cut_{j},axiom,{cands[i][0]} = {cands[i][1]}).\n'
                                                   for j, i in enumerate(proved)])
        return cpath

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
        if a.lemma_fold and rnd > 0:
            # (unfold.py) folded instances of the lemma axioms: where a lemma subterm unifies with a
            # definition's body, the lemma under the unifier, folded (twee reaches these critical
            # pairs of a lemma with a definition rule late or never; goal 212 of aK2_eq_aK3_r)
            import unfold
            txt = open(path).read()
            add = unfold.lemma_fold_text(txt, limit=a.lemma_fold)
            if add:
                path = os.path.join(self.dir, 'tmp', tag + '.f.p')
                with open(path, 'w') as f:
                    f.write(txt.rstrip('\n') + '\n' + add)
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
        if a.p9loop and a.p9_share and '__goal_' in name:
            # Bigloop-style sharing between siblings: matchers of the failed runs of goals at most
            # P9_SHARE places away. Only from unconditional goals (a universally quantified unit
            # equation): twee never infers from their negated goal, so their matchers are theorems
            # of the shared axioms and proven lemmas. (A conditional goal's hypotheses are axioms
            # of its run, so its matchers can depend on them.) The goal's own matchers come last,
            # so --p9-max keeps them first.
            import lemmas
            o, k = lemmas.split(name)
            seen, extra = set(p9), []
            for dd in range(1, a.p9_share + 1):
                for j in (k - dd, k + dd):
                    m = f'{o}__goal_{j}'
                    if m not in self.p9_uncond:
                        try:
                            self.p9_uncond[m] = lemmas.unit_eq(lemmas.conjecture(m) or '~')
                        except OSError:
                            self.p9_uncond[m] = False
                    if self.p9_uncond[m]:
                        for f in self.p9_lemmas(m):
                            if f not in seen:
                                seen.add(f); extra.append(f)
            p9 = extra + p9
        if a.p9_max and len(p9) > a.p9_max:
            p9 = p9[-a.p9_max:]   # the most recently derived
        if p9:
            txt = open(path).read().rstrip('\n') + '\n' + ''.join(
                f'fof(p9lemma_{i}, axiom, {f}).\n' for i, f in enumerate(p9))
            path = os.path.join(self.dir, 'tmp', tag + '.p')
            with open(path, 'w') as f:
                f.write(txt)
        go = getattr(self, 'goal_override', {}).get(name)
        if go:
            # (climb.py --updown) a weakened goal: an instance of the conjecture in its place
            txt = ''.join(x for x in open(path) if not x.startswith('fof(goals,conjecture,')) + \
                f'fof(goals,conjecture,{go}).\n'
            path = os.path.join(self.dir, 'tmp', tag + '.w.p')
            with open(path, 'w') as f:
                f.write(txt)
        extra = getattr(self, 'extra_axioms', {}).get(name)
        if extra:
            # (climb.py) assumed statements: extra axioms (label, TPTP formula) of this run
            txt = open(path).read().rstrip('\n') + '\n' + ''.join(
                f'fof({lab}, axiom, {f}).\n' for lab, f in extra)
            path = os.path.join(self.dir, 'tmp', tag + '.p')
            with open(path, 'w') as f:
                f.write(txt)
        if a.unfold:
            # (unfold.py) the definitions substituted away: twee's KBO folds them, Prover9 unfolds;
            # some stalled goals are a rewrite step apart once unfolded. Hints are unfolded with the
            # problem's definitions (proofs of unfolded runs give unfolded hints; folded runs
            # normalise them back with the definition rules).
            import unfold
            txt, defs = unfold.unfold_text(open(path).read(),
                                           only=None if a.unfold == 'all' else set(a.unfold.split(',')))
            path = os.path.join(self.dir, 'tmp', tag + '.u.p')
            with open(path, 'w') as f:
                f.write(txt)
            if hints and defs:
                hints = [tuple(unfold.unfold_eq(x, defs) for x in h[:2]) + tuple(h[2:]) for h in hints]
        if a.gen_model and resume is True:
            if a.gen_cuts:
                path = self.gen_cuts_problem(name, path, tag, hints)
            else:
                hints = self.gen_hints(name, hints)
        args = a.args.split()
        if max_cpu is not None:
            args = [x for i, x in enumerate(args) if x != '--max-cpu' and (i == 0 or args[i - 1] != '--max-cpu')]
            args += ['--max-cpu', str(max_cpu)]
        cmd = [a.twee, path, '--max-time', str(T), '--no-colour', '--quiet',
               '--no-proof', '--print-hints', '--print-given'] + args
        if a.p9loop:
            cmd += ['--print-hint-matchers']
        if a.gen_model:   # (twee-e39) the given rules of a failed run, for gen_save
            cmd += ['--print-given-unsolved']
        cap = name in getattr(self, 'capture_given', ())
        if cap and not a.gen_model:   # (climb.py) the final run's given rules, also when it fails
            cmd += ['--print-given-unsolved']
        k = 0
        if a.p9_orders > 1:
            # P9loop's term orderings: attempt k of a goal (rounds from --start, or the number of
            # its earlier p9 attempts) uses ordering k mod N; ordering 0 is twee's default
            # (Bigloop, --p9-parallel P: the P runs of a round take orderings attempt*P .. attempt*P+P-1)
            k = (self.p9_attempt(name, rnd) * max(1, a.p9_parallel) + variant + a.p9_order_offset) % a.p9_orders
            if k:
                cmd += ['--precedence', ','.join(self.p9_precedence(orig_path, k))]
        if self.model:
            m, v, gdir = self.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, name)] + \
                   a.model_args.split()
        if hints and a.stall:
            cmd += ['--eqhint-stall', str(a.stall)]
        spath = os.path.join(self.dir, 'states', name + '.bin')
        if resume:   # True: continue the saved state; 'fresh': start over but save (replaces the old state);
            # 'nosave': start over and keep no state (an older one is removed: it is of an older context)
            if resume not in ('fresh', 'nosave') and os.path.exists(spath):
                cmd += ['--load-state', spath]
            if resume != 'nosave':
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
            try:
                os.unlink(hpath)
            except FileNotFoundError:
                pass
        if cap:
            sig_ = self.signature(name)   # (in the hints' canonical form)
            self.captured[name] = [canon_key(x[0], x[1], sig_) for x in givenlib.parse_given_parents(out)
                                   if x and x[0] != x[1]]
        ok = 'HINTS-END' in out
        if ok and getattr(self, 'chains', None) is not None:
            self.chains.add_record(name, out)   # (--chain-level: the new proof's lemma record)
        if ok and hasattr(self, 'used'):
            # (climb.py) the axiom and lemma names the proof uses
            for line in out.splitlines():
                if line.startswith('USEDAXIOMS'):
                    self.used[tag] = set(line.split()[1:])
            self.assumed[tag] = hintlib.extract_assumed(out)
        heap = 'Heap exhausted' in out   # (twee's default heap limit, -M6g, or +RTS -M in --args)
        if heap and resume and os.path.exists(spath):
            # a resumed state that ran out of heap (seen: a saved state plus one new lemma axiom
            # exploding) would do it again at the next level, so the goal starts over
            os.unlink(spath)
        if a.gen_model and not ok:
            self.gen_save(name, out, path)
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
            if ok or resume == 'nosave':
                for p in (spath, spath + '.tmp'):
                    if os.path.exists(p):
                        os.unlink(p)
            elif os.path.exists(spath + '.tmp'):
                os.replace(spath + '.tmp', spath)
        stats = ''
        for line in out.splitlines():
            if line.startswith('HINTSTATS'):
                stats = line
        if heap:
            stats += ' HEAP'
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

    def after_hints(self, n):
        """--hint-after K: the statements of the next K unsolved unit goals of N's original, as
        hints (unproven, so never as axioms; hints do not affect soundness)."""
        import lemmas, unfold
        if not hasattr(self, '_goals_by_orig'):
            self._goals_by_orig = collections.defaultdict(list)
            for f in os.listdir(PROB):
                if '__goal_' in f and f.endswith('.p'):
                    o_, k_ = lemmas.split(f[:-2])
                    self._goals_by_orig[o_].append(k_)
            for v in self._goals_by_orig.values():
                v.sort()
        o, k = lemmas.split(n)
        out = []
        for j in self._goals_by_orig.get(o, []):
            if len(out) >= self.a.hint_after:
                break
            m = f'{o}__goal_{j}'
            if j <= k or m in self.solved:
                continue
            f = lemmas.conjecture(m)
            e = unfold.eq_of(f) if f and lemmas.unit_eq(f) else None
            if e:
                out.append((unfold.show(e[0]), unfold.show(e[1])))
        return out

    def make_lemma_index(self):
        """The kNN lemma index over the proven goals; --lemma-pop: similarity weighted by lemma use counts, from
        --lemma-uses DIRS (then the loop's own goals are left out of the counts) or else from this loop's outputs."""
        import lemmas
        a = self.a
        uses = None
        if a.lemma_pop:
            if a.lemma_uses:
                uses = lemmas.lemma_uses(a.lemma_uses.split(','), exclude=set(self.names))
            else:
                uses = lemmas.lemma_uses([self.dir])
        deps = lemmas.proof_deps(os.path.join(self.dir, 'hints'), sorted(self.solved)) if a.lemma_deps else None
        return lemmas.LemmaIndex(sorted(self.solved), subsets=a.lemma_subsets, uses=uses, pop=a.lemma_pop,
                                 deps=deps, dep_w=a.lemma_deps, dep_n=a.lemma_dep_n)

    def deep_hints(self, n, lev, pools):
        """A deeper level's hints: with --chain-level, from that level on the goal's chain (sibchain.py) once
        the records are in, else (or when the chain is empty) the usual hints."""
        a = self.a
        C = getattr(self, 'chains', None)
        if C is not None and lev >= a.chain_level and C.ready() and '__goal_' in n:
            import lemmas
            o, _ = lemmas.split(n)
            hs = C.chain(n, self.lemma_src.get(o, set()), a.chain_sibs, a.chain_max)
            if hs:
                return hs
        return self.hints_for(n, pools, None)

    def hints_for(self, n, pools, knn):
        a = self.a
        hs = self.hints_for1(n, pools, knn)
        if a.hint_after:
            seen = set((h[0], h[1]) for h in hs)
            hs = hs + [h for h in self.after_hints(n) if h not in seen]
        if a.hint_lemma_proofs:
            hs = hs + self.lemma_proof_hints(n, set((h[0], h[1]) for h in hs))
        return hs

    def lemma_proof_hints(self, n, seen):
        """(16 Nov, --hint-lemma-proofs F) the proof steps of N's kNN lemmas (proven goals of the same or weaker
        axioms, mostly of other originals) as hints with score factor F, after N's own pool"""
        import lemmas
        a = self.a
        if not a.lemma_knn or getattr(self, 'lemma_index', None) is None or not getattr(self, 'lemma_src', None):
            return []
        out = []
        for src in lemmas.knn_picks(n, self.lemma_src, a.lemmas, self.lemma_index, a.lemma_knn, a.lemma_after):
            try:
                lines = open(os.path.join(self.dir, 'hints', src)).read().splitlines()
            except OSError:
                continue
            for x in lines[:a.hint_lemma_proof_max]:
                w = x.split('\t')
                if len(w) >= 2 and (w[0], w[1]) not in seen:
                    seen.add((w[0], w[1])); out.append((w[0], w[1], str(a.hint_lemma_proofs)))
        return out

    def hints_for1(self, n, pools, knn):
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
            self.lemma_index = self.make_lemma_index()
        if a.chain_level >= 0:
            # (18 Nov, exp3/exp8) runs at level >= --chain-level take the chain of the goal's nearest proven
            # siblings below as hints (sibchain.py), not the original's pool; records load in the background
            import sibchain
            self.chains = sibchain.Chains(self.dir, records=a.chain_records or None)
            print(f'  cascade: --chain-level {a.chain_level}: chain hints of the {a.chain_sibs} nearest proven siblings'
                  f' (records {a.chain_records or "of this loop"})', flush=True)
        # --retry-knn (15 Nov): fresh 20 s runs in the full current context proved 6 of 35 goals the
        # cascade held as stalled (~30 proofs/CPU-h); all six used kNN lemmas from other originals
        # proven since their last run, a change the sibling context and pool growth do not see
        knn_at, knn_cur, kgen = {}, {}, [0, time.time(), len(self.solved)]
        kfile = os.path.join(self.dir, 'knn_at.tsv')
        RK = a.retry_knn and a.lemma_knn
        if RK and os.path.exists(kfile):
            for l in open(kfile):
                w = l.rstrip('\n').split('\t')
                if len(w) == 2 and l.endswith('\n'):
                    knn_at[w[0]] = frozenset(filter(None, w[1].split(',')))
        def knn_sig(n):
            v = knn_cur.get(n)
            if v is None or v[0] != kgen[0]:
                v = knn_cur[n] = (kgen[0], frozenset(lemmas.knn_picks(n, self.lemma_src, a.lemmas, self.lemma_index,
                                                                      a.lemma_knn, a.lemma_after)))
            return v[1]
        def knnch(n):
            return RK and (n not in knn_at or knn_sig(n) != knn_at[n])
        kf = open(kfile, 'a') if RK else None
        if RK:
            print(f'  cascade: --retry-knn: {len(knn_at)} goals with a recorded kNN lemma set', flush=True)
        byo = collections.defaultdict(list)   # the set's goals and the proven goals of their originals
        for n in set(self.names) | set(self.solved):
            if '__goal_' in n:
                byo[orig_of(n)].append(n)
        origs = {orig_of(n) for n in self.names}
        byo = {o: L for o, L in byo.items() if o in origs}
        for o in byo:
            byo[o].sort(key=lambda n: lemmas.split(n)[1])
        srt = {}   # original -> sorted proven goal numbers (dropped when a proof arrives)
        # ctx() runs for every waiting goal several times in every pass (Z0, 51,784 goals from zero: 43M
        # calls, most of the dispatcher's time, 6 of 12 workers idle), so it is cached per original and
        # dropped with srt
        ctxc = {}   # original -> {(name, after): ctx}
        gnum = {n: lemmas.split(n) for n in self.names if "__goal_" in n}   # name -> (original, goal number)
        def heads():
            hs = set()
            for L in byo.values():
                for i in range(len(L) - 1, -1, -1):
                    if L[i] in self.solved:
                        if i + 1 < len(L):
                            hs.add(L[i + 1])
                        break
                else:
                    hs.add(L[0])
            return hs
        def ctx(n, after=None):
            o, k = gnum[n] if n in gnum else lemmas.split(n)
            c_ = ctxc.get(o)
            if c_ is None:
                c_ = ctxc[o] = {}
            v_ = c_.get((n, after))
            if v_ is None:
                v_ = c_[(n, after)] = ctx_(o, k, after)
            return v_
        def ctx_(o, k, after):
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
        # --line-gaps R,F: distances in lines of the original Prover9 proof (AIM60k's LADR files
        # name each goal's proof line). The goals were picked in stripes 3..55 lines apart, so a
        # gap of one goal can be 3 lines or 55; success falls with the line distance (UL r5:
        # L0 retries 32% within 13 lines, 12% beyond 21).
        gl = {}
        if a.line_gaps:
            R, F = (int(x) for x in a.line_gaps.split(','))
            for l in open(a.goal_lines):
                n, x = l.split()
                gl[n] = int(x)
        def gaps():
            """unsolved goal -> (places after the nearest proven goal below it (in the set),
            proof lines after it (with --line-gaps; else the places again))."""
            g = {}
            for o, L in byo.items():
                last = None
                for i, n in enumerate(L):
                    if n in self.solved:
                        last = i
                    elif last is None:
                        g[n] = (10**6, 10**6)
                    else:
                        g[n] = (i - last, gl[n] - gl[L[last]] if gl else i - last)
            return g
        def may_retry(n, g):
            return g[n][0] <= a.retry_gap or (gl and g[n][1] <= R)
        def may_deepen(n, g):
            return g[n][0] <= a.frontier or (gl and g[n][1] <= F)
        # --cascade-start -1: nothing tried yet, so the goals near a proof all get a T0 run first
        # --cascade-was-below: the earlier attempts had lemmas from below only, so with
        # --lemma-after exactly the goals that now get lemmas from above are retried
        att = {n: ((ctx(n, False if a.cascade_was_below else None), a.cascade_start) if a.cascade_start >= 0
                   else (None, -1))
               for n in self.names if n not in self.solved}
        running = {}   # future -> (name, level)
        nf = collections.Counter()   # goal -> its failed fresh (T0) runs in this round (--fail-order)
        nfb = {}   # --fail-reset: goal -> its places after the nearest proven goal below at its last failure
        # --orig-rate: (original, fresh run?) -> its runs' proofs and runs, each older run weighing 0.9 per
        # newer one of the same original and kind (about its last 10), and the last 500 of each kind overall
        ors = collections.defaultdict(float); orc = collections.defaultdict(float)
        org = {True: collections.deque(maxlen=500), False: collections.deque(maxlen=500)}
        origs = sorted({v[0] for v in gnum.values()})
        ob0, obd = {}, {}
        def orate(o):
            """the original's estimated proof rates: a fresh run, a deeper level (the latter's prior is the
            former scaled by the overall ratio)"""
            G0 = org[True]; p0 = (sum(G0) + 1) / (len(G0) + 10)
            GD = org[False]; pd = (sum(GD) + 1) / (len(GD) + 10)
            v0 = (ors[(o, True)] + 5 * p0) / (orc[(o, True)] + 5)
            return v0, (ors[(o, False)] + 5 * v0 * pd / p0) / (orc[(o, False)] + 5)
        rdir = os.path.join(self.dir, 'r%d' % rnd); os.makedirs(rdir, exist_ok=True)
        if a.cascade_continue and os.path.exists(os.path.join(rdir, 'results.tsv')):
            # a restarted round: the levels this round already tried (in the current context)
            k0 = 0; fresh = set(); kc = 0
            for ri, line in enumerate(open(os.path.join(rdir, 'results.tsv'))):
                f = line.rstrip('\n').split('\t')
                if len(f) >= 5 and f[0] in att and f[4][:1] == 'L' and f[4][1:].isdigit():
                    lev = int(f[4][1:])
                    if a.chain_since_row and ri < a.chain_since_row and lev >= max(1, a.chain_level):
                        # (--chain-since-row R: a deep run before row R had the pool's hints; the goal gets
                        # its chain-level run again, fresh with the chain; 1,032 unsolved goals at 11:55)
                        lev = max(0, a.chain_level - 1); kc += 1
                    if lev == 0:
                        fresh.add(f[0])
                        if f[1] == 'NO':
                            nf[f[0]] += 1
                    if lev > att[f[0]][1]:
                        att[f[0]] = (ctx(f[0]), lev); k0 += 1
            print(f'  cascade: continuing round {rnd}, {k0} level updates from its results'
                  + (f' ({kc} deep rows before row {a.chain_since_row} capped below --chain-level)' if a.chain_since_row else ''),
                  flush=True)
            if a.fresh_first:
                # a goal with no fresh run in this round only resumed states of earlier rounds and
                # contexts (--cascade-start 0): a fresh T0 run first (on 97 goals that failed L1 this
                # way, fresh 20 s proved 28/63 of those without one, 8/34 of the others)
                # (a count of its own: nf is the --fail-order counter; UL40 died on it, 17 Nov 16:24)
                nff = 0
                for n in att:
                    if n not in fresh:
                        att[n] = (None, -1); nff += 1
                print(f'  cascade: --fresh-first: {nff} goals without a fresh run in round {rnd}', flush=True)
        # --retry-hints G: also retry (fresh, at T0) a goal whose original's hint pool has grown by
        # the factor G since its last fresh run. Resuming does not use new hints well (the saved
        # queue was scored without them): on 32 gap-1 goals that failed L1, resuming to 320 s
        # proved 0/13, a fresh 80 s run 8/32, mostly goals whose pool had grown by 25% or more.
        hp = {}   # goal -> size of its pool at its last fresh run
        def psz(n):
            return len(pools.get(self.pool_key(n), ()))
        if a.retry_hints:
            # history: hints= of each goal's last fresh run, relative to the latest run of its pool
            lastL0, latest = {}, {}
            for r in range(1, rnd + 1):
                p = os.path.join(self.dir, 'r%d' % r, 'results.tsv')
                if not os.path.exists(p):
                    continue
                for line in open(p):
                    f = line.rstrip('\n').split('\t')
                    m = re.search(r'hints=(\d+)', f[3]) if len(f) >= 4 else None
                    if not m:
                        continue
                    h = int(m.group(1)); latest[self.pool_key(f[0])] = h
                    if (f[4] if len(f) >= 5 and f[4][:1] == 'L' else 'L0') == 'L0':
                        lastL0[f[0]] = h
            for n in att:
                k = self.pool_key(n)
                hp[n] = psz(n) * lastL0[n] / latest[k] if n in lastL0 and latest.get(k) else psz(n)
            print(f'  cascade: hint pools grown by {a.retry_hints}x since the last fresh run: '
                  f'{sum(1 for n in att if psz(n) >= hp[n] * a.retry_hints)} goals', flush=True)
        def grown(n):
            return a.retry_hints and psz(n) >= hp[n] * a.retry_hints
        # --sched-model M: order the fresh runs by a model's predicted success (schedmodel.py on
        # schedfeats.py features). Above all it weighs whether the nearest proven goal below
        # changed since the goal's last failed fresh run (UL r5: 43% then, 11-15% otherwise,
        # at any distance); on the last 40% of r5 its top quarter proved 43% vs 29% by distance.
        SM = H = None; sc = {}; over = collections.Counter(); startctx = {}; calib = [0.0, 0, 0]
        auto0 = collections.deque(maxlen=a.sched_pmin_auto or 1)   # (ok, wall s, predicted p) of fresh runs
        auto1 = collections.deque(maxlen=a.sched_pmin_auto or 1)   # (ok, wall s, 0) of resumes
        if a.sched_model:
            import schedfeats, schedmodel
            SM = schedmodel.load_model(a.sched_model)
            gl_ = gl or {l.split()[0]: int(l.split()[1]) for l in open(a.goal_lines)}
            H = schedfeats.History(self.names, gl_, c6='nfail_c6' in SM['feats'])
            t_ = time.time(); H.replay(self.dir); H.R.set_solved(self.solved)
            lmin = math.log(a.sched_pmin / (1 - a.sched_pmin))
            print(f'  cascade: --sched-model: history replayed in {time.time()-t_:.0f}s', flush=True)
        def score(n):
            o = orig_of(n); v = sc.get(n)
            if v is None or v[0] != over[o]:
                x_ = H.feats(n)[0]
                v = sc[n] = (over[o], schedmodel.score(SM, x_), x_['lgap'])
            return v[1]
        t0 = time.time(); new = 0; done_n = 0
        def add_proof(n, rnd, dt, hs):
            if H:
                H.add(n); over[orig_of(n)] += 1
            att.pop(n, None)
            self.solved[n] = (rnd, dt)
            key = self.pool_key(n)
            cnt[key].update(hs)
            self.count_uncond(n, hs)
            pools[key] = [h for h, _ in cnt[key].most_common()]
            o, k = lemmas.split(n)
            self.lemma_src[o] = self.lemma_src.get(o, set()) | {k}
            srt.pop(o, None); ctxc.pop(o, None)
        # --sync: proofs that other processes (climb.py --live, merge.py) append to solved.tsv
        # after writing their hints file join the pools and lemmas as if found here
        sync_f = open(os.path.join(self.dir, 'solved.tsv'), 'rb')
        sync_f.seek(self.solved_off); sync_t = 0; nsync = 0
        def sync():
            nonlocal nsync
            while True:
                pos = sync_f.tell()
                line = sync_f.readline().decode('utf8', 'replace')
                if not line.endswith('\n'):   # (none, or a row still being written: read it next time)
                    sync_f.seek(pos)
                    break
                w = line.rstrip('\n').split('\t')
                if len(w) < 2 or w[0] in self.solved:
                    continue
                hp_ = os.path.join(self.dir, 'hints', w[0])
                if not os.path.exists(hp_):
                    continue
                hs = [tuple(x.rstrip('\n').split('\t')[:2]) for x in open(hp_) if '\t' in x]
                add_proof(w[0], rnd, float(w[2]) if len(w) > 2 else 0.0, hs)
                nsync += 1
        with open(os.path.join(rdir, 'results.tsv'), 'a') as rf, \
             open(os.path.join(self.dir, 'solved.tsv'), 'a') as sf, \
             ThreadPoolExecutor(a.j) as ex:
            tm = [0.0, 0.0, 0.0, 0.0]   # the main thread's seconds: scheduling passes, submitting, waiting, results
            t_r = None
            retry, deep, far, light, last_full = [], [], [], False, -1e18
            pdur = 0.0   # the last full pass's seconds (without a kNN index rebuild)
            # --mix M: runs of three kinds, near retries (r), goals beyond the retry gaps (f: far, and goals
            # never run) and deeper levels (d); each kind with waiting goals keeps M of the workers, the
            # other slots go to the kind with the most proofs per run second over its last 300 runs; the
            # seconds its running jobs have taken so far count as spent without a proof (a 320 s resume takes
            # ~25 wall minutes: until one ended, the prior kept the deeper levels first, ul39 17 Nov)
            ycls = {c: collections.deque(maxlen=300) for c in 'rfd'}; rcls = {}; ncls = collections.Counter()
            rt0 = {}   # future -> its start
            def yld(c):
                now = time.time()
                return (sum(x[0] for x in ycls[c]) + 0.5) / (sum(x[1] for x in ycls[c]) + 5.0
                                                             + sum(now - rt0[f] for f in rt0 if rcls.get(f) == c))
            while True:
                if t_r is not None:
                    tm[3] += time.time() - t_r
                if a.sync and time.time() - sync_t >= a.sync:
                    sync(); sync_t = time.time()
                busy = {n for n, _ in running.values()}
                tq_ = time.time()
                if tq_ - t0 < a.cascade_hours * 3600:
                    # --pass-every S: the full pass (every waiting goal: gaps, contexts, pools; on 51,784 goals
                    # from zero 134 of the main thread's 180 s) at most every S seconds; between them the
                    # lists it made are used up, each goal checked again when it is taken
                    # (and at most every 8 times the last full pass's length: --fail-order's list of every
                    # waiting goal took 0.2-0.35 s a pass, Z3 kept 5-7 of its 12 workers busy, REPORT 2at)
                    light = bool(a.pass_every and (retry or deep or far)
                                 and tq_ - last_full < max(a.pass_every, 8 * pdur))
                    if not light:
                        last_full = tq_; krb = 0.0
                        g = gaps()
                        if a.orig_rate:
                            # (in bins of 0.1, all above 0.9 in one: from zero, when nearly every run proves,
                            # the order stays nearest first; the learned scheduler's per-original ranking
                            # starved originals there, 2aq)
                            for o in origs:
                                v0, vd = orate(o); ob0[o] = -min(9, int(10 * v0)); obd[o] = -min(9, int(10 * vd))
                        if RK and (time.time() - kgen[1] >= a.knn_refresh or len(self.solved) - kgen[2] >= 300):
                            t_ = time.time()
                            self.lemma_index = self.make_lemma_index()
                            kgen[:] = [kgen[0] + 1, time.time(), len(self.solved)]; krb = time.time() - t_
                            print(f'  cascade: --retry-knn: kNN index rebuilt ({len(self.solved)} proofs, '
                                  f'{time.time()-t_:.0f}s)', flush=True)
                        if SM and RK:
                            # best predicted first; the kNN check (~27 ms a goal) only as far as needed
                            free = a.j - len(running)
                            retry = []; cand = {}; kbudget = [150]   # (uncached kNN checks per pass: ~4 s)
                            def kcheck(n):
                                v_ = knn_cur.get(n)
                                if v_ is None or v_[0] != kgen[0]:
                                    if kbudget[0] <= 0:
                                        return False
                                    kbudget[0] -= 1
                                return knnch(n)
                            for v, n in sorted((-score(n), n) for n in att if n not in busy):
                                if ctx(n) != att[n][0] or grown(n) or n not in knn_at:
                                    cand[n] = -v
                                elif -v >= lmin and sc[n][2] <= a.sched_max_lgap and len(retry) < free and kcheck(n):
                                    cand[n] = -v
                                else:
                                    continue
                                if -v >= lmin and sc[n][2] <= a.sched_max_lgap and len(retry) < free:
                                    retry.append((v, n))
                        elif SM:
                            cand = {n: score(n) for n in att
                                    if n not in busy and (ctx(n) != att[n][0] or grown(n))}
                            retry = sorted((-v, n) for n, v in cand.items()
                                           if v >= lmin and sc[n][2] <= a.sched_max_lgap)
                        elif a.fail_order:
                            # --fail-order: every goal with a new context (with --far-retry also those beyond
                            # the retry gaps) in one list, fewest failed fresh runs first, then near before
                            # far, then nearest. In Z1's second hour a goal's first run proved 51% (365 proofs
                            # per run hour), one that had failed before 4-6% (17-29 an hour), on 61% of the
                            # workers' time; Z2 after 30 min 88% (1,749 an hour) against 7-17% (52-106)
                            nfg = nf.get; fr = a.fail_reset; nbg = nfb.get; obg = ob0.get
                            retry = sorted((nfg(n, 0) if not fr or nbg(n) == g[n][0] else 0,
                                            obg(gnum[n][0], 0), 0 if may_retry(n, g) else 1, g[n][1], gnum[n][1], n) for n in att
                                           if n not in busy and (ctx(n) != att[n][0] or grown(n))
                                           and (a.far_retry or may_retry(n, g)))
                        else:
                            retry = sorted((g[n][1], gnum[n][1], n) for n in att
                                           if n not in busy and (ctx(n) != att[n][0] or grown(n)) and may_retry(n, g))
                        uset = set()
                        if SM and a.sweep_first:
                            # --sweep-first: goals never run in this round go first, in goal order across the
                            # originals. The scheduler's model was trained on retries; from zero it ranked one
                            # original's goals first and starved the others (LZ4, 16 Nov: 427 runs, all of
                            # a_of_aa, 232 proofs at 10 min against 806 without the scheduler)
                            un = [n for _, _, n in sorted((gnum[n][1], gnum[n][0], n) for n in att
                                                          if n not in busy and att[n] == (None, -1))]
                            if un:
                                uset = set(un)
                                retry = [(0, n) for n in un] + [x for x in retry if x[-1] not in uset]
                        deep_running = collections.Counter(orig_of(n) for n, l in running.values() if l > 0)
                        # --head-first: an original's tail head (the goal after its last proven goal)
                        # deepens first, and only heads go to levels >= --head-only-from. A head's
                        # proof starts a chain (the goal above gets a new context, ~50%); at 06:45 the 95
                        # heads held 4,851 of the 8,335 unsolved goals behind them, and 93 had never run
                        # beyond 80 s (median 416 wall s in all)
                        # (hds, not hs: a run's result reuses hs for its hints, None when it failed; ORE and ORF
                        # died on `n in hs` after 70 min, 17 Nov 14:15)
                        hds = heads() if a.head_first else set()
                        # (heads first for the levels below --head-only-from, at any level: a head's
                        # 320 s resume, ~30% x a chain of ~2, pays about as well per CPU-second as an
                        # 80 s resume of another goal, ~20%; at 06:58 2,185 goals waited for one)
                        hof = a.head_only_from or len(T)
                        deep = sorted((int(not (n in hds and att[n][1] + 1 < hof)), att[n][1] + 1,
                                       obd.get(gnum[n][0], 0), deep_running[gnum[n][0]], g[n][1], gnum[n][1], n)
                                      for n in att
                                      if n not in busy and ctx(n) == att[n][0] and att[n][1] + 1 < len(T)
                                      and (may_deepen(n, g) or n in hds) and not grown(n)
                                      and (n in hds or not a.head_only_from or att[n][1] + 1 < a.head_only_from))
                        far = []
                        if SM and a.far_retry and (a.mix or len(running) + len(retry) + len(deep) < a.j):
                            far = sorted((-v, n) for n, v in cand.items()
                                         if (v < lmin or sc[n][2] > a.sched_max_lgap) and n not in uset)[:a.j]
                        elif a.far_retry and not (a.fail_order and not SM) and (a.mix or len(running) + len(retry) + len(deep) < a.j):
                            # --far-retry: idle slots retry (fresh) the goals beyond the retry gaps too,
                            # nearest first, after everything else
                            far = heapq.nsmallest(a.j, ((g[n][1], gnum[n][1], n) for n in att
                                                        if n not in busy and (ctx(n) != att[n][0] or grown(n))
                                                        and not may_retry(n, g)))
                    if not light:
                        pdur = max(0.0, time.time() - tq_ - krb)
                    tm[0] += time.time() - tq_; tq_ = time.time()
                    while len(running) < a.j and (retry or deep or far):
                        if a.mix:
                            cn_ = collections.Counter(rcls.values())
                            av = [c for c, L in (('r', retry), ('f', far), ('d', deep)) if L
                                  and (c != 'd' or cn_['d'] < a.j - a.reserve)]
                            if not av:
                                break
                            low = [c for c in av if cn_[c] < a.mix * a.j]
                            cl = min(low, key=lambda c: cn_[c]) if low else max(av, key=yld)
                        else:
                            cl = ('r' if retry else 'f') if retry or (far and not deep) else 'd'
                        if cl != 'd':
                            n = (retry if cl == 'r' else far).pop(0)[-1]; lev = 0
                            # (never a goal already running: a full pass's lists predate this pass's own
                            # submissions, so a goal taken as deep first came round again as a retry; both runs
                            # share tmp/<goal>.hints, and ul44 died on the second unlink, 18 Nov 09:29)
                            if any(m == n for m, _ in running.values()):
                                continue
                            if light and (n not in att or n in busy or not (ctx(n) != att[n][0] or grown(n))):
                                continue
                            att[n] = (ctx(n), 0)
                            if RK:
                                knn_at[n] = knn_sig(n)
                                kf.write(f'{n}\t{",".join(sorted(knn_at[n]))}\n'); kf.flush()
                            if a.retry_hints:
                                hp[n] = psz(n)
                            # fresh in the new context; its state replaces any older one, so deepening
                            # continues this search
                            # (--p9loop: no states; the goal's matcher lemmas carry over instead)
                            # (--lean-states: a goal that may not deepen now keeps no state; a 10 MB state
                            # took 20-30% of a failing 5 s run's wall time, and 97% of Z4's 13,427 were never
                            # resumed; were it to deepen later, its next level starts over with the full budget)
                            # (--no-fresh-states: no fresh run keeps one; in the second hour of ORE, 2,000 runs,
                            # failing fresh runs took 68% of the workers' time and only 1% of runs resumed)
                            keep = (not a.no_fresh_states and
                                    (not a.lean_states or len(T) < 2 or may_deepen(n, g) or n in hds))
                            fut = ex.submit(self.run_one, n, self.hints_for(n, pools, None), rnd,
                                            T[0], False if a.p9loop else ('fresh' if keep else 'nosave'),
                                            a.cascade_cpu * T[0])
                        else:
                            if sum(1 for _, l in running.values() if l > 0) >= a.j - a.reserve:
                                break
                            x_ = deep.pop(0); lev, n = x_[1], x_[-1]
                            if any(m == n for m, _ in running.values()):
                                continue
                            if light and (n not in att or att[n][1] + 1 != lev or ctx(n) != att[n][0] or grown(n)):
                                continue
                            att[n] = (ctx(n), lev)
                            sp = os.path.join(self.dir, 'states', n + '.bin')
                            # --p9loop (P9loop deepening): a fresh run of the level's increment, with the
                            # matcher lemmas of the goal's earlier runs and its next ordering, not a resume
                            # (--chain-level L: level L runs fresh with the chain, the setting exp3/exp8 tested;
                            # resuming the 5 s pool state kept the queue's pool scores, --no-resume-requeue, so
                            # the chain reached only new pairs; ul43/ul44 ran that way, 08:28-12:00)
                            fc = (getattr(self, 'chains', None) is not None and lev == a.chain_level
                                  and not a.p9loop)
                            b = T[lev] if fc else (T[lev] - T[lev - 1] if (a.p9loop or os.path.exists(sp)) else T[lev])
                            fut = ex.submit(self.run_one, n, self.deep_hints(n, lev, pools), rnd,
                                            b, 'fresh' if fc else not a.p9loop, a.cascade_cpu * b)
                        running[fut] = (n, lev); rcls[fut] = cl; ncls[cl] += 1; rt0[fut] = time.time()
                        if H and lev == 0:   # (its features, context and predicted success, for observe())
                            x_, c_ = H.feats(n)
                            startctx[n] = (c_, 1 / (1 + math.exp(-score(n))), x_)
                    tm[1] += time.time() - tq_
                    if light and len(running) < a.j and not (retry or deep or far):
                        last_full = -1e18; t_r = None   # (the kept lists ran dry: a full pass now)
                        continue
                if not running:
                    if a.sync and time.time() - t0 < a.cascade_hours * 3600:
                        # nothing to run: wait for proofs from the side workers (new contexts)
                        time.sleep(a.sync); sync(); sync_t = time.time()
                        continue
                    break
                tq_ = time.time()
                fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
                tm[2] += time.time() - tq_; t_r = time.time()
                for f in fin:
                    n0, lev = running.pop(f)
                    n, ok, dt, stats, hs = f.result()
                    ycls[rcls.pop(f, 'r')].append((1 if ok else 0, dt)); rt0.pop(f, None)
                    if a.orig_rate:
                        k_ = (orig_of(n), lev == 0)
                        ors[k_] = ors[k_] * 0.9 + (1 if ok else 0); orc[k_] = orc[k_] * 0.9 + 1
                        org[lev == 0].append(1 if ok else 0)
                    if lev == 0 and not ok:
                        if a.fail_reset:
                            # (counted since the nearest proven goal below last changed)
                            gb = g[n][0] if n in g else None
                            nf[n] = nf[n] + 1 if nfb.get(n) == gb else 1; nfb[n] = gb
                        else:
                            nf[n] += 1
                    done_n += 1
                    if H:
                        c_, p_, x_ = startctx.pop(n, (None, 0.0, None)) if lev == 0 else (None, 0.0, None)
                        H.observe(n, ok, 'L%d' % lev, c_, x_); over[orig_of(n)] += 1
                        if lev == 0:
                            calib[0] += p_; calib[1] += 1; calib[2] += ok
                            if a.sched_retrain and calib[1] % a.sched_retrain == 0:
                                # the runs the model picks drift from those it learned on
                                # (ABb: 81+ lines with a new context 21%, predicted 25%)
                                SM = schedmodel.train_rows(H.rows, SM['feats'], recent=a.sched_recent)
                                sc.clear()
                                print(f'  cascade: --sched-retrain: model retrained on {len(H.rows)} rows', flush=True)
                    if H and a.sched_pmin_auto:
                        (auto0 if lev == 0 else auto1).append((ok, dt, p_ if lev == 0 else 0.0))
                    rf.write(f'{n}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{stats}\tL{lev}\tt={time.time()-t0:.0f}\n'); rf.flush()
                    if ok and n in self.solved:
                        pass   # (synced from another process meanwhile: keep its row and hints)
                    elif ok:
                        new += 1
                        with open(os.path.join(self.dir, 'hints', n), 'w') as hf:
                            for l, r in hs:
                                hf.write(f'{l}\t{r}\n')
                        sf.write(f'{n}\t{rnd}\t{dt:.2f}\n'); sf.flush()
                        add_proof(n, rnd, dt, hs)
                    if done_n % 50 == 0 and H and a.sched_pmin_auto and len(auto0) >= 100 and len(auto1) >= 50:
                        # --sched-pmin-auto: a fresh run pays as well as a resume when its actual success
                        # p0 = (resume proofs per wall second) x (mean fresh wall seconds); the scheduler's
                        # p is calibrated by (fresh proofs / fresh predicted) over the window
                        r1 = sum(x[0] for x in auto1) / max(1e-9, sum(x[1] for x in auto1))
                        c0 = sum(x[1] for x in auto0) / len(auto0)
                        k = sum(x[0] for x in auto0) / max(1e-9, sum(x[2] for x in auto0))
                        pm = min(0.3, max(0.003, r1 * c0 / max(k, 0.05)))
                        lmin = math.log(pm / (1 - pm))
                        print(f'  cascade: --sched-pmin-auto: {pm:.4f} (resumes {r1*3600:.2f} proofs/h, '
                              f'fresh {c0:.1f} s, calibration {k:.2f})', flush=True)
                    if done_n % 50 == 0:
                        print(f'  cascade: {done_n} runs, new={new}, {len(running)} running, '
                              f'{time.time()-t0:.0f}s' + (f', synced={nsync}' if a.sync else '')
                              + f', main s: pass {tm[0]:.0f} submit {tm[1]:.0f} wait {tm[2]:.0f} results {tm[3]:.0f}'
                              + (', mix ' + ' '.join(f'{c} {ncls[c]} {3600*yld(c):.0f}/h' for c in 'rfd') if a.mix else '')
                              + (f', fresh {calib[2]}/{calib[1]} (predicted {calib[0]:.0f})' if H else ''),
                              file=sys.stderr, flush=True)
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
                self.lemma_index = self.make_lemma_index()
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

def make_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('set')
    ap.add_argument('dir')
    ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--timeout', default='2', help='seconds, or a list per round: 2,8,30')
    ap.add_argument('--model', action='store_true', help='train and use the ENIGMA rule model')
    ap.add_argument('--model-args', default='--rule-threshold 0.1 --rule-penalty 2')
    ap.add_argument('--chain-level', type=int, default=-1,
                    help='(18 Nov) cascade levels >= L take the chain of the goal\'s nearest proven siblings below as hints '
                         '(their proofs expanded through the proven goals they used; sibchain.py) instead of the pool')
    ap.add_argument('--chain-sibs', type=int, default=10, help='--chain-level: how many nearest proven siblings')
    ap.add_argument('--chain-max', type=int, default=100000, help='--chain-level: at most this many chain hints')
    ap.add_argument('--chain-since-row', type=int, default=0,
                    help='--chain-level with --cascade-continue: deep rows of the round before this row (pool-era runs) '
                         'are ignored, so those goals get a fresh chain-level run')
    ap.add_argument('--chain-records', default='',
                    help='--chain-level: a records file of sibchain.py --build (all loops; default: this loop\'s outputs)')
    ap.add_argument('--retry-knn', action='store_true',
                    help='--cascade: a change in a goal\'s kNN lemmas (--lemma-knn) since its last fresh run makes it '
                         'eligible for a fresh retry, like a new sibling context; the kNN index is rebuilt every '
                         '--knn-refresh seconds. Sets used are kept in DIR/knn_at.tsv; goals without one count as changed')
    ap.add_argument('--knn-refresh', type=float, default=1800)
    ap.add_argument('--given-extra', help='more given dirs (comma-separated) for training')
    ap.add_argument('--gen-model', help='(gen.py) hint generator: a failed run saves its context; '
                    'the resumed next level adds --gen-n generated hints')
    ap.add_argument('--gen-n', type=int, default=200)
    ap.add_argument('--gen-ctx', type=int, default=256)
    ap.add_argument('--gen-temp', type=float, default=1.0)
    ap.add_argument('--gen-python', default='/project/hintwork/venv/bin/python3')
    ap.add_argument('--gen-script', default='gen.py', help='gen.py, or gencopy.py (the copy-action model)')
    ap.add_argument('--gen-cuts', type=int, default=0, help='with --gen-model: the K most sampled equations as cuts '
                    '(proved in one --multi-goal run, then axioms of the resumed level) instead of hints')
    ap.add_argument('--gen-cut-time', type=float, default=5.0)
    ap.add_argument('--gen-cut-sep', action='store_true', help='--gen-cuts: each cut in its own run with its own kNN lemmas and rule-model goal')
    ap.add_argument('--gen-cut-min', type=int, default=1, help='a cut counts when proved after this many considered CPs')
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
    ap.add_argument('--lemma-deps', type=float, default=0.0,
                    help='--lemma-knn, MaSh-style: also score the lemmas that the nearest proven goals\' proofs have '
                         'as steps, with this weight (lemmas.proof_deps)')
    ap.add_argument('--lemma-dep-n', type=int, default=50, help='--lemma-deps: the number of nearest proven goals')
    ap.add_argument('--lemma-pop', type=float, default=0.0,
                    help='--lemma-knn: multiply a candidate lemma\'s similarity by 1 + POP * log(1 + its uses in proofs)')
    ap.add_argument('--lemma-uses', default='',
                    help='--lemma-pop: count uses in these loop dirs (comma list; the run\'s own goals left out) '
                         'instead of this loop\'s outputs')
    ap.add_argument('--lemma-knn', type=int, default=0,
                    help='rounds > 0: also add up to K proven goals with the same axioms (any original) most similar to the goal')
    ap.add_argument('--model-theory', action='store_true',
                    help='rule model with the ENIGMA theory block (rulemodel.py --theory; e.g. models/rm4t)')
    ap.add_argument('--lemma-after', action='store_true',
                    help='sibling lemmas are the nearest proven goals above N as well as below (all proven '
                         'before the run, so still well-founded)')
    ap.add_argument('--unfold', nargs='?', const='all', default=None, metavar='F,G,..',
                    help='substitute the problem\'s definitions (f(X1..Xn) = t) away in the axioms, lemmas, '
                         'conjecture and hints (unfold.py); only those of F, G, .. if given')
    ap.add_argument('--hint-lemma-proofs', type=float, default=0.0, metavar='F',
                    help='also use the proof steps of each kNN lemma (--lemma-knn) as hints, with score factor F')
    ap.add_argument('--hint-lemma-proof-max', type=int, default=300, metavar='M',
                    help='--hint-lemma-proofs: at most M steps from each lemma\'s proof')
    ap.add_argument('--hint-after', type=int, default=0, metavar='K',
                    help='also use the statements of the next K unsolved unit goals of the original as hints')
    ap.add_argument('--lemma-fold', type=int, default=0, metavar='K',
                    help='add up to K folded instances of each lemma axiom (unfold.lemma_fold_text)')
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
    ap.add_argument('--retry-hints', type=float, default=0,
                    help='G: --cascade also retries goals whose hint pool grew by the factor G since their last fresh run')
    ap.add_argument('--p9-order-offset', type=int, default=0,
                    help='--p9-orders: shift the ordering index (e.g. 1: a single round runs ordering 1, not the default)')
    ap.add_argument('--line-gaps', default='',
                    help='R,F: --cascade also retries goals at most R proof lines after a proven sibling, '
                         'deepens goals at most F lines after one, and orders both by proof lines')
    ap.add_argument('--goal-lines', default='/project/hintwork/abs/goal_lines.tsv',
                    help='goal name -> line of the original proof (from AIM60k/problems/ladr)')
    ap.add_argument('--cascade-continue', action='store_true',
                    help='--cascade: a restarted round; goals count as tried at the levels its results.tsv shows')
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
    ap.add_argument('--p9-share', type=int, default=0,
                    help='--p9loop: also take the matchers of unconditional sibling goals at most this many places away')
    ap.add_argument('--p9-max', type=int, default=0, help='--p9loop: at most this many lemmas, the most recently derived (0 = all)')
    ap.add_argument('--init', help='import round-0 results (solved.tsv and hints) of another loop dir')
    ap.add_argument('--pass-every', type=float, default=0, metavar='S',
                    help='--cascade: the full scheduling pass at most every S seconds, the lists it made used up '
                         'in between (from zero on 51,784 goals the pass took 75%% of the main thread)')
    ap.add_argument('--mix', type=float, default=0,
                    help='--cascade: near retries, goals beyond the retry gaps (also never run) and deeper levels '
                         'each keep this share of the workers while they have waiting goals; the other slots go to '
                         'the kind with the most proofs per run second lately (with --far-retry; from zero on '
                         '51,784 goals the near retries took every slot and 12,998 goals never ran, REPORT 2as)')
    ap.add_argument('--fail-order', action='store_true',
                    help='--cascade without --sched-model: the fresh (T0) runs in one list, goals with the fewest '
                         'failed fresh runs in the round first, then those within the retry gaps, then the nearest '
                         '(with --far-retry also the goals beyond the gaps; a first run proved 51%% in Z1\'s second '
                         'hour, a repeat 4-6%%, REPORT 2as)')
    ap.add_argument('--lean-states', action='store_true',
                    help='--cascade: a fresh run of a goal that may not deepen now (beyond --frontier and the '
                         'line gap, not a head) keeps no state (with twee-e43, which keeps none for a proved goal)')
    ap.add_argument('--no-fresh-states', action='store_true',
                    help='--cascade: no fresh run keeps a state; a goal\'s first deeper level starts over with its '
                         'full budget (the deeper levels keep theirs)')
    ap.add_argument('--orig-rate', action='store_true',
                    help='--cascade: within --fail-order\'s failure counts, and within each deeper level, goals of '
                         'originals whose recent runs of that kind proved most go first (in bins of 0.1; Z4 after '
                         '30,000 runs: the top fifth of fresh runs by this rate proved 50%%, the rest 10%%, AUC 0.84; '
                         'production\'s 80 s resumes 29%% against 12%%)')
    ap.add_argument('--fail-reset', action='store_true',
                    help='--fail-order: a goal\'s failures count from the last change of the nearest proven goal '
                         'below it (Z1 after 30 min: a repeat after such a change proved 13.1%%, 62 an hour, '
                         'otherwise 5.2%%, 23 an hour; far first runs in Z4\'s second hour 8-12%%)')
    ap.add_argument('--far-retry', action='store_true',
                    help='--cascade: slots with nothing else to run retry goals beyond the retry gaps '
                         '(fresh at T0, nearest first) when their context or pool changed')
    ap.add_argument('--fresh-first', action='store_true',
                    help='--cascade-continue: goals without a T0 (fresh) run in the round get one first')
    ap.add_argument('--sync', type=float, default=0,
                    help='--cascade: every S seconds, take in the proofs other processes appended to '
                         'solved.tsv (after writing hints/NAME), e.g. climb.py --live or merge.py')
    ap.add_argument('--sched-model',
                    help='--cascade: order the fresh runs by this model\'s predicted success '
                         '(schedmodel.py train), any distance; below --sched-pmin they wait for --far-retry')
    ap.add_argument('--sched-retrain', type=int, default=0,
                    help='--sched-model: retrain the model on the replayed and new fresh runs every N fresh runs')
    ap.add_argument('--sched-recent', type=int, default=0,
                    help='--sched-retrain: on the last N fresh runs only (0 = all of rounds 3 on)')
    ap.add_argument('--sched-max-lgap', type=int, default=10**6,
                    help='--sched-model: goals farther than this (proof lines) from a proof below go '
                         'after the resumes (ABb: 700 lines away 6/132 proved)')
    ap.add_argument('--head-first', action='store_true',
                    help='--cascade: tail heads (the goal after the last proven goal of an original) '
                         'deepen first, up to the levels below --head-only-from')
    ap.add_argument('--head-only-from', type=int, default=0,
                    help='--head-first: only tail heads go to levels >= L (e.g. 3 with --cascade 10,80,320,1280)')
    ap.add_argument('--sweep-first', action='store_true',
                    help='--sched-model: goals never run in this round get their fresh run first, in goal order '
                         '(from zero the model alone starves originals without proofs)')
    ap.add_argument('--sched-pmin-auto', type=int, default=0, metavar='W',
                    help='--sched-model: set --sched-pmin online from the last W fresh runs and W resumes: '
                         'the predicted success at which a fresh run pays as well per wall second as a resume')
    ap.add_argument('--sched-pmin', type=float, default=0.06,
                    help='--sched-model: fresh runs predicted below this go after the resumes (default 0.06: '
                         'an L1 resume proves ~17%% in 3x the time of a fresh run)')
    return ap

def init_dir(a):
    if a.init and not os.path.exists(os.path.join(a.dir, 'solved.tsv')):
        import shutil
        os.makedirs(os.path.join(a.dir, 'hints'), exist_ok=True)
        with open(os.path.join(a.dir, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(a.init, 'solved.tsv')):
                if l.split('\t')[1] == '0':
                    f.write(l)
                    n = l.split('\t')[0]
                    shutil.copy(os.path.join(a.init, 'hints', n), os.path.join(a.dir, 'hints', n))

def main():
    a = make_parser().parse_args()
    init_dir(a)
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
