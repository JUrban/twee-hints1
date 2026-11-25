#!/usr/bin/env python3
"""Sketch climbing (Veroff's sketches as a search over sets of assumptions).

For a target goal T = X__goal_N, the candidate assumptions are the statements
of the M nearest unproven sibling goals (steps of the same Prover9 proof, so
true, but not yet proven by us), nearest in proof lines, on either side.

The climb starts at the top of the lattice (all candidates assumed) and goes
down. Each run is T with an assumption set S as extra axioms, plus the
production context (proven sibling lemmas, kNN lemmas, the original's hint
pool, the rule model) and the sketch hints collected so far for the original.
A proof tells which assumptions it used (USEDAXIOMS), U. Its steps become
sketch hints of the original (shared by its targets). Then the sets U minus
one element are queued (smallest first). A proof with no assumption is a real
proof of T. Unless one is found, the climb ends with a real run of T with all
sketch hints.

Assumptions only change the problems that produce hints. Hints only guide
the search, so the real proofs are sound.

climb.py SET DIR [--m M] [--sketch-time S] [--final-time F] [--runs R] [-j J]
         -- <loop.py options for the production context>
Writes DIR/climb.tsv (one line per run) and, for real proofs, DIR/solved.tsv
and DIR/hints/<goal> as loop.py does.
"""
import argparse, collections, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, hintsel, loop, lemmas


VAR = re.compile(r'\bX\d+\b')
CONST = re.compile(r'\b([a-z][A-Za-z0-9_]*)\b(?!\s*\()')   # (constants: lower-case names not applied)
_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[(),=]")


HERE = os.path.dirname(os.path.abspath(__file__))

def short(x):
    return x[len('assume_'):]


def parse_term(toks, i):
    """(term, next index); a term is a variable name (capitalised) or (f, [args])."""
    t = toks[i]
    if i + 1 < len(toks) and toks[i + 1] == '(':
        args, i = [], i + 2
        while True:
            a, i = parse_term(toks, i)
            args.append(a)
            if toks[i] == ',':
                i += 1
            else:
                return (t, args), i + 1
    return (t if t[0].isupper() else (t, [])), i + 1


TWEE = '/project/bin/twee-e37'
_laws = {}
_laws_lock = threading.Lock()
def laws(t):
    """Simplifying laws over the axioms' signature (Veroff's sketch assumptions, possibly false):
    commutativity of binary operations, associativity of the binary operations the axioms do not
    define, and each defined operation (an axiom f(X1..Xn) = s, distinct variables, f not in s)
    equal to a constant of the axioms or to its first argument."""
    path = os.path.join(lemmas.PROB, t + '.p')
    ar, consts, defined = {}, set(), set()
    for line in open(path):
        if not (line.startswith('cnf(') and ',axiom,' in line):
            continue
        body = line.split(',axiom,', 1)[1].rsplit(')', 1)[0]
        toks = _tok.findall(body)
        try:
            lhs, i = parse_term(toks, 0)
            rhs, _ = parse_term(toks, i + 1)
        except (IndexError, ValueError):
            continue
        def walk(x):
            if isinstance(x, tuple):
                ar[x[0]] = len(x[1])
                if not x[1]:
                    consts.add(x[0])
                for y in x[1]:
                    walk(y)
        walk(lhs); walk(rhs)
        def syms(x):
            return {x[0]} | set().union(*map(syms, x[1])) if isinstance(x, tuple) else set()
        if isinstance(lhs, tuple) and lhs[1] and all(isinstance(v, str) for v in lhs[1]) \
                and len(set(lhs[1])) == len(lhs[1]) and lhs[0] not in syms(rhs):
            defined.add(lhs[0])
    key = (tuple(sorted(ar.items())), tuple(sorted(consts)), tuple(sorted(defined)))
    with _laws_lock:
        if key not in _laws:
            _laws[key] = _make_laws(path, ar, consts, defined)
        return _laws[key]


def _make_laws(path, ar, consts, defined):
    res = {}
    for f, n in sorted(ar.items()):
        if n == 2:
            res[f'assume_law_comm_{f}'] = f'! [X,Y] : {f}(X,Y) = {f}(Y,X)'
            if f not in defined:
                res[f'assume_law_assoc_{f}'] = f'! [X,Y,Z] : {f}({f}(X,Y),Z) = {f}(X,{f}(Y,Z))'
        if f in defined and n >= 1:
            vs = ','.join(f'X{i}' for i in range(n))
            for e in sorted(consts):
                res[f'assume_law_{f}_is_{e}'] = f'! [{vs}] : {f}({vs}) = {e}'
            res[f'assume_law_{f}_is_x'] = f'! [{vs}] : {f}({vs}) = X0'
    # drop the laws that collapse the theory (prove X = Y with the axioms): with one of them
    # every sketch is trivial and its hints are worthless
    ax = ''.join(l for l in open(path) if l.startswith('cnf(') and ',axiom,' in l)
    keep = {}
    for lab, f in res.items():
        tmp = os.path.join('/tmp' if not os.environ.get('TMPDIR') else os.environ['TMPDIR'],
                           f'climb_collapse_{os.getpid()}_{lab}.p')
        with open(tmp, 'w') as fh:
            fh.write(ax + f'fof({lab}, axiom, {f}).\nfof(collapse, conjecture, ! [X,Y] : X = Y).\n')
        try:
            o = subprocess.run([TWEE, tmp, '--max-time', '2', '--abstract-time', '2000', '--quiet', '--no-proof'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120).stdout.decode()
        except subprocess.TimeoutExpired:
            o = ''
        os.unlink(tmp)
        if 'Theorem' not in o:
            keep[lab] = f
    print(f'laws: {len(keep)} of {len(res)} kept, collapsing: {sorted(short(x) for x in res if x not in keep)}', flush=True)
    return keep


_thy = {}
_thy_lock = threading.Lock()
def theories(t, k, info=None, explore=0, meta=None, ts=None):
    """(--theories, user's suggestion 15 Nov: assume a stronger theory, e.g. Bol loops for loops) the extra
    axioms of the K originals' theories that strictly contain T's axioms, fewest extra axioms first, one
    group per distinct theory: [{label: TPTP formula}]. Stronger theories are mathematically relevant and
    consistent, so they should not trivialise a sketch the way laws do."""
    A = lemmas.axiom_set(t)
    with _thy_lock:
        if not _thy:
            for f in sorted(os.listdir(lemmas.PROB)):
                o = f.rpartition('__goal_')[0]
                if o and o not in _thy:
                    _thy[o] = f[:-2]
    groups = {}
    for o, n in _thy.items():
        B = lemmas.axiom_set(n)
        if A < B and B not in groups:
            extra = []
            for l in open(os.path.join(lemmas.PROB, n + '.p')):
                if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l:
                    body = l.split(',', 2)[2].rsplit(')', 1)[0].strip()
                    if re.sub(r'\s+', '', body) in A:
                        continue
                    if l.startswith('cnf('):
                        vs = sorted(set(re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', body)))
                        body = (f'! [{",".join(vs)}] : ({body})' if vs else body)
                    extra.append(body)
            groups[B] = [0.0, len(extra), o, extra]
    if info and groups:
        # rank by the most similar solved goal of the theory (INFO: name -> (axiom key, goal features))
        import hintsel
        try:
            F = frozenset(hintsel.goal_features(t, 3))
        except Exception:
            F = frozenset()
        bo = {o: lemmas.axiom_set(n) for o, n in _thy.items()}
        for m, (_, G) in info.items():
            B = bo.get(m.rpartition('__goal_')[0])
            if B in groups and F and G:
                sim = len(F & G) / len(F | G)
                if sim > -groups[B][0]:
                    groups[B][0] = -sim
    out = []
    byB = {id(v): B for B, v in groups.items()}
    ranked = sorted(groups.values(), key=lambda x: (x[0], x[1], x[2]))
    if ts is not None:
        # (--theory-ts) Thompson sampling: rank by a draw from each theory's Beta posterior of its nontrivial
        # sketch rate (prior mean 0.2, weight 2), so the good theories come first and the untried get tried
        import random as _r
        rng = _r.Random()
        th = {id(v): rng.betavariate(0.4 + ts.get(v[2], (0, 0))[0],
                                     1.6 + ts.get(v[2], (0, 0))[1] - ts.get(v[2], (0, 0))[0]) for v in ranked}
        ranked.sort(key=lambda v: -th[id(v)])
        explore = 0
    # (--theory-explore R) the last R of the K slots take theories drawn at random from the rest, seeded by
    # the target, so the logs cover more than the heuristic's top (data for learning the theory choice)
    h = max(0, k - explore)
    rest = ranked[h:]
    R = min(explore, len(rest)) if len(ranked) > k else 0
    import random as _r
    pick = ranked[:h] + _r.Random(t).sample(rest, R) if R else ranked[:k]
    for j, v in enumerate(pick):
        out.append((byB[id(v)], {f'assume_thy_{j}_{i}': f for i, f in enumerate(v[3])}))
        if meta is not None:
            meta.append((j, v[2], -v[0], v[1], 2 if ts is not None else int(R > 0 and j >= h),
                         sorted(groups.values(), key=lambda x: (x[0], x[1], x[2])).index(v), len(ranked),
                         ' & '.join(v[3])))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('dir')
    ap.add_argument('--m', type=int, default=8, help='candidate assumptions per target')
    ap.add_argument('--sketch-time', type=float, default=5)
    ap.add_argument('--final-time', type=float, default=20)
    ap.add_argument('--final-cpu', type=float, default=0,
                    help='(23 Nov, exp67\'s controls) the final run\'s CPU cap in seconds (twee --max-cpu) in place of 10 x\n'
                         '--final-time; with a large --final-time, the final runs for this much CPU (CPU-matched controls)')
    ap.add_argument('--max-sketch-time', type=float, default=None,
                    help='cap of the doubled sketch budget (default 4 x --sketch-time); a top set that fails '
                         'at the cap ends the climb')
    ap.add_argument('--runs', type=int, default=8, help='sketch runs per target (before the final run)')
    ap.add_argument('--side', default='both', choices=['both', 'below', 'after'])
    ap.add_argument('--laws', action='store_true',
                    help='also assume simplifying laws (possibly false), as Veroff: commutativity and '
                         'associativity of binary operations, derived operations trivial')
    ap.add_argument('--freq', type=int, default=0,
                    help='also assume the K most frequent equations of the original\'s proofs (unconditional goals)')
    ap.add_argument('--knn', type=int, default=0,
                    help='also assume the K unproven goals of other originals (axioms a subset of the '
                         'target\'s) most similar to the target: lines of Prover9 proofs, so true')
    ap.add_argument('--fill', type=float, default=0,
                    help='Veroff\'s gap filling: after each sketch proof, one twee --multi-goal run of this '
                         'many seconds tries to prove the proof\'s lemmas that depend on the assumptions, without '
                         'them; the proven ones become axioms (true lemmas) of the later runs on the original\'s goals')
    ap.add_argument('--theories', type=int, default=0,
                    help="assume the extra axioms of up to K stronger theories (other originals' axiom sets that "
                         "strictly contain the target's), one theory at a time")
    ap.add_argument('--chain', action='store_true', help='--updown: a proof becomes a sibling lemma and hints of the later targets at once')
    ap.add_argument('--updown', action='store_true', help='climb up (theory unions, weaker goals) when no sketch proves the target, then down')
    ap.add_argument('--move-model', help='--updown: a latticepolicy.py model orders the moves (softmax sampling)')
    ap.add_argument('--move-temp', type=float, default=1.0)
    ap.add_argument('--heads-only', action='store_true',
                    help='--live --reclimb-heads: climb only the heads (each original\'s first unsolved goal)')
    ap.add_argument('--reclimb-heads', type=int, default=0,
                    help='--live: climb each original\'s first unsolved goal up to N times, interleaved with new targets')
    ap.add_argument('--theory-ts', action='store_true',
                    help='--theories: rank the stronger theories by Thompson sampling of their nontrivial-sketch rate')
    ap.add_argument('--theory-ts-ab', action='store_true', help='--theory-ts only on targets with bit 1 of crc32')
    ap.add_argument('--theory-explore', type=int, default=0,
                    help='--theories K: the last R slots go to random other stronger theories (seeded by target)')
    # (23 Nov, exp67) --targets FILE: in set mode, climb only these goals (a frozen head list), so two settings can be
    # compared on the same targets outside production
    ap.add_argument('--targets', default='', help='set mode: climb only the goals listed in FILE')
    ap.add_argument('--move-ab', action='store_true', help='--move-model only on targets of odd crc32 (A/B test)')
    # (24 Nov) --final-only-ab: targets with bit 2 of crc32 of the name set get no sketch runs (the final only, with the
    # climb hints their original already has, their siblings' climbs included), the others the full climb: does a target's
    # climb add to its long final? (exp76 +1 -0, exp67 nil)
    ap.add_argument('--final-only-ab', action='store_true', help='no sketch runs on targets with bit 2 of crc32 (A/B test)')
    ap.add_argument('--move-eps', type=float, default=0.1, help='--move-model: share of uniformly random moves')
    ap.add_argument('--up-single', action='store_true', help='--updown: going up also adds one assumption at a time')
    ap.add_argument('--up-levels', type=int, default=2, help='--up-single: levels of one-more-axiom')
    ap.add_argument('--up-beam', type=int, default=2, help='--up-single: failed sets extended per level')
    ap.add_argument('--up-width', type=int, default=4, help='--up-single: single additions per extended set')
    ap.add_argument('--weaken', type=int, default=4, help='--updown: weaker goals (instances) to try')
    ap.add_argument('--theory-lemmas', type=int, default=10, help='--theories: proven goals of the stronger theory as assumptions too')
    ap.add_argument('--gen-assume', type=int, default=0, help='assume the generator\'s K most sampled equations, one at a time')
    ap.add_argument('--gen-ctx-dir', default='/project/hintwork/loops/GC1A/genctx')
    ap.add_argument('--gen-model', default='/project/hintwork/models/gc1_4000.pt')
    ap.add_argument('--gen-python', default='/project/hintwork/venv/bin/python3')
    ap.add_argument('--gen-n', type=int, default=400)
    ap.add_argument('--gen-temp', type=float, default=0.7)
    ap.add_argument('--min-sketch-steps', type=int, default=0,
                    help='a sketch proof that uses laws and has fewer steps bans those laws for the target '
                         '(the climb restarts from the top without them): laws that trivialise give no hints')
    ap.add_argument('--fill-max', type=int, default=40, help='dependent lemmas per --fill check')
    ap.add_argument('--true-max', type=int, default=60, help='true lemmas (from --fill) per original')
    ap.add_argument('-j', type=int, default=2)
    ap.add_argument('--goal-lines', default='/project/hintwork/abs/goal_lines.tsv')
    ap.add_argument('--live', metavar='LOOPDIR',
                    help='side worker of a running loop.py --cascade --sync: climb its stalled goals (a failed '
                         'deepening run L1+ is the goal\'s last result in its latest round, unsolved), nearest '
                         'proven goal below first; real proofs go into LOOPDIR (hints, then a solved.tsv row). '
                         'DIR gets a copy of LOOPDIR\'s solved.tsv (remove it to restart with a fresh copy) '
                         'and a link to its hints. SET: sets/all (the rule model\'s goal files).')
    ap.add_argument('--refresh', type=float, default=1800, help='--live: seconds between context refreshes')
    ap.add_argument('--exclude', default='', help='--live: comma-separated goal list files to skip')
    # (24 Nov) --reclimb FILE: goals there may be climbed again while they have fewer than 2 finals, after the new targets,
    # nearest proven goal below first: CLS71's targets whose 20 s final failed get one climb with the current final time
    # (exp76: 160 s finals proved 2 of 30 such targets)
    ap.add_argument('--reclimb', default='', help='--live: goals that may be climbed once more (fewer than 2 finals)')
    # (25 Nov) the time ladder: a rung re-runs goals that already had finals in this dir
    ap.add_argument('--reclimb-max', type=int, default=2, help='--reclimb: while fewer than N finals in DIR (default 2)')
    ap.add_argument('--cpus', type=int, default=0,
                    help='--live: start a climb only while fewer than N twee processes run on the machine '
                         '(own ones included), so the climber fills the CPUs the loop leaves idle; -j caps it')
    argv = sys.argv[1:]
    i = argv.index('--') if '--' in argv else len(argv)
    c = ap.parse_args(argv[:i])
    rest = argv[i + 1:]   # loop.py options for the production context
    a = loop.make_parser().parse_args([c.set, c.dir] + rest)
    if c.live and not os.path.exists(os.path.join(c.dir, 'solved.tsv')):
        os.makedirs(c.dir, exist_ok=True)
        if not os.path.lexists(os.path.join(c.dir, 'hints')):
            os.symlink(os.path.abspath(os.path.join(c.live, 'hints')), os.path.join(c.dir, 'hints'))
        with open(os.path.join(c.dir, 'solved.tsv'), 'w') as f:
            for l in open(os.path.join(c.live, 'solved.tsv')):
                w = l.split('\t')
                if len(w) >= 3 and l.endswith('\n'):
                    f.write(f'{w[0]}\t0\t{w[2].strip()}\n')
    loop.init_dir(a)
    lp = loop.Loop(a)
    lp.used = {}; lp.extra_axioms = {}; lp.assumed = {}; lp.capture_given = set(); lp.captured = {}
    gl = {l.split()[0]: int(l.split()[1]) for l in open(c.goal_lines)}
    allgoals = lemmas.by_original(gl)
    pools = lp.build_pools()
    if a.model:
        lp.train_model(1)
    lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
    if a.lemma_knn:
        lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
    cands = {}
    ix = {}
    if c.knn:
        ix['u'] = lemmas.LemmaIndex(sorted(n for n in gl if n not in lp.solved), subsets=True)
    # equation counts over the proofs of unconditional goals of the targets' originals (--freq):
    # a conditional goal's hypotheses become false 'hints' like X0 = X1 when generalised
    ucnt = collections.defaultdict(collections.Counter)
    if c.freq:
        keys = {lp.pool_key(t) for t in lp.names}
        for n in lp.solved:
            if '__goal_' in n and lp.pool_key(n) in keys:
                f = lemmas.conjecture(n)
                if f and lemmas.unit_eq(f):
                    ucnt[lp.pool_key(n)].update((h[0], h[1]) for h in lp.hints_of(n))
    sketch = collections.defaultdict(list)   # original -> sketch hints (canonical pairs), oldest first
    true = collections.defaultdict(dict)     # original -> {TPTP formula: label} of lemmas --fill proved
    tkey = {}                                # (original, label) -> the true lemma as a canonical hint pair
    checked = collections.defaultdict(set)   # original -> dependent lemmas --fill tried
    fo = open(os.path.join(c.dir, 'fill.tsv'), 'a')
    seen = collections.defaultdict(set)
    lock = threading.Lock()
    # (19 Nov 17:00; user: "the climber runs should probably be kept ... and we should keep their stats") what used to
    # live only in memory goes to disk, and a restart reloads it:
    #   true.tsv           original, label, TPTP formula, lhs, rhs (canonical), target, tag: each lemma --fill proved
    #   fillhints/<t>/<tag> the steps of the fill run's real proofs
    #   assume.tsv         target, climb prefix, label, source goal (or -), formula: what each assumption label meant
    #                      (kNN labels are positions in a list that changes as goals get proved)
    #   used.tsv           target, tag, every axiom label a proof used (lemma_goal_J, lemma_knn_I_<goal>, assume_*,
    #                      true_*): a conditional proof's full premises, so it can be replayed once they are proven;
    #                      (24 Nov) then label=source goal for each assume_*, and 1 if the proof was of a weakened goal
    ft = open(os.path.join(c.dir, 'true.tsv'), 'a'); fa = open(os.path.join(c.dir, 'assume.tsv'), 'a')
    fu = open(os.path.join(c.dir, 'used.tsv'), 'a')
    #   fillattempts.tsv   original, formula, proved (0/1), target, tag: every gap --fill tried (which are fillable)
    ffa = open(os.path.join(c.dir, 'fillattempts.tsv'), 'a')
    #   fillprem.tsv       original, true label, formula, target, tag, premises: for each lemma --fill proved, the
    #                      axiom and lemma names the fill run's proofs used (twee's USEDAXIOMS, all the run's proved
    #                      gaps together: a superset of this lemma's), or, without that line, every lemma name in
    #                      the fill problem. (23 Nov) trust.py checks fill lemmas by it (before, none was recorded,
    #                      and production's proofs with lemma_fill_N axioms in exposed originals stayed untrusted).
    fpr = open(os.path.join(c.dir, 'fillprem.tsv'), 'a')
    csrc = {}   # (target, label) -> the goal an assumption states
    nre = [0, 0]
    for l_ in (open(os.path.join(c.dir, 'true.tsv')) if os.path.getsize(os.path.join(c.dir, 'true.tsv')) else ()):
        w_ = l_.rstrip('\n').split('\t')
        if len(w_) >= 5 and w_[2] not in true[w_[0]]:
            true[w_[0]][w_[2]] = w_[1]; tkey[(w_[0], w_[1])] = (w_[3], w_[4]); checked[w_[0]].add(w_[2]); nre[0] += 1
    for sub_ in ('fillhints', 'sketches'):   # (real hints first, as online)
        d0_ = os.path.join(c.dir, sub_)
        for t_ in (sorted(os.listdir(d0_)) if os.path.isdir(d0_) else ()):
            o_ = lemmas.split(t_)[0]
            for g_ in sorted(os.listdir(os.path.join(d0_, t_))):
                for l_ in open(os.path.join(d0_, t_, g_)):
                    w_ = l_.rstrip('\n').split('\t')
                    if l_.startswith('#') or len(w_) < 2:
                        continue
                    k_ = (w_[0], w_[1])
                    if k_ not in seen[o_]:
                        seen[o_].add(k_); sketch[o_].append(k_); nre[1] += 1
    if any(nre):
        print(f'reloaded {nre[0]} true lemmas and {nre[1]} sketch hints of {len(sketch)} originals', flush=True)
    # (--theory-ts) per theory (its representative original): [nontrivial single-theory sketches, such sketches],
    # from this dir's logs and then online; tmeta: target -> {slot: theory}
    thy_stats = collections.defaultdict(lambda: [0, 0]); tmeta = {}
    if c.theory_ts and os.path.exists(os.path.join(c.dir, 'theories.tsv')):
        import latticedata
        for r_ in latticedata.theory_rows(c.dir, c.min_sketch_steps or 30):
            thy_stats[r_['theory']][0] += r_['nontrivial']; thy_stats[r_['theory']][1] += r_['moves']
        print(f'--theory-ts: {len(thy_stats)} theories, {sum(v[1] for v in thy_stats.values())} sketches from the logs',
              flush=True)
    out = open(os.path.join(c.dir, 'climb.tsv'), 'a')
    sf = open(os.path.join(c.dir, 'solved.tsv'), 'a')

    def ts_arm(t):
        """--theory-ts-ab: the targets that rank theories by Thompson sampling (bit 1 of the original's crc32, independent of
        --move-ab's bit 0); without --theory-ts-ab all of them"""
        import zlib
        return not c.theory_ts_ab or (zlib.crc32(lemmas.split(t)[0].encode()) >> 1) % 2 == 1

    def candidates(t):
        """label -> TPTP formula of each candidate assumption of target T."""
        o, k = lemmas.split(t)
        pr = lp.lemma_src.get(o, set())
        js = [j for j in allgoals.get(o, ()) if j != k and j not in pr
              and (c.side == 'both' or (c.side == 'below') == (j < k))]
        js.sort(key=lambda j: (abs(gl[f'{o}__goal_{j}'] - gl[t]), j))
        res = {}
        for j in js:
            if sum(1 for x in res if x.startswith('assume_goal_')) >= c.m:
                break
            f = lemmas.conjecture(f'{o}__goal_{j}')
            if f and lemmas.unit_eq(f):   # (a conditional goal's statement is not an equation)
                res[f'assume_goal_{j}'] = f
        if c.knn:
            with lock:
                near = ix['u'].select(t, c.knn, exclude={f'{o}__goal_{j}' for j in allgoals.get(o, ())})
            for i, m in enumerate(near):
                res[f'assume_knn_{i}'] = lemmas.conjecture(m); csrc[(t, f'assume_knn_{i}')] = m
        if c.laws:
            res.update(laws(t))
        if c.gen_assume:
            # (--gen-assume, user 15 Nov: dream up new axioms with the generator) its K most sampled
            # equations for T, from T's saved context (--gen-ctx-dir), each tried alone; possibly false
            cp = os.path.join(c.gen_ctx_dir, t)
            if os.path.exists(cp):
                cmd = [c.gen_python, os.path.join(HERE, 'gencopy.py'), 'hints', cp, t, '--load', c.gen_model,
                       '--n', str(c.gen_n), '--threads', '1', '--temp', str(c.gen_temp), '--counts', '1']
                try:
                    p_ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=300)
                    rows = [x.split('\t') for x in p_.stdout.decode().splitlines()]
                except subprocess.TimeoutExpired:
                    rows = []
                gl_ = []
                for w in rows:
                    if len(w) < 2:
                        continue
                    vs = sorted(set(VAR.findall(w[0] + ' ' + w[1])), key=lambda v: int(v[1:]))
                    f = (f'! [{",".join(vs)}] : ' if vs else '') + f'{w[0]} = {w[1]}'
                    if f == lemmas.conjecture(t):
                        continue
                    lab = f'assume_gen_{len(gl_)}'
                    res[lab] = f; gl_.append(frozenset([lab]))
                    if len(gl_) >= c.gen_assume:
                        break
                tgroups[t] = tgroups.get(t, []) + gl_
        if c.theories:
            li = getattr(lp, 'lemma_index', None)
            meta = []
            with lock:
                ts_ = {o: tuple(v) for o, v in thy_stats.items()} if c.theory_ts and ts_arm(t) else None
            groups = theories(t, c.theories, li.info if li is not None else None, c.theory_explore, meta, ts_)
            tmeta[t] = {m_[0]: m_[1] for m_ in meta}
            with lock, open(os.path.join(c.dir, 'theories.tsv'), 'a') as f_:   # (for learning the theory choice)
                f_.writelines('\t'.join(map(str, (t,) + m_)) + '\n' for m_ in meta)
            A = lemmas.axiom_set(t)
            for j, (B, g) in enumerate(groups):
                if li is not None and c.theory_lemmas:
                    # theorems of B: its originals' proven goals most similar to T (true in B only)
                    for i, m in enumerate(li.select_in(t, c.theory_lemmas, B, A)):
                        f = lemmas.lemma_form(m)
                        if f:
                            g[f'assume_thy_{j}_lem{i}'] = f
                res.update(g)
            tgroups[t] = tgroups.get(t, []) + [frozenset(g) for _, g in groups]
        if c.freq:
            cnt = ucnt.get(lp.pool_key(t), collections.Counter())
            i = 0
            for (l, r), n in cnt.most_common():
                if i >= c.freq or n < 3:
                    break
                if VAR.fullmatch(l) and VAR.fullmatch(r):
                    continue   # X0 = X1 would collapse everything
                vs = sorted(set(VAR.findall(l + ' ' + r)), key=lambda v: int(v[1:]))
                res[f'assume_freq_{i}'] = (f'! [{",".join(vs)}] : ' if vs else '') + f'{l} = {r}'
                i += 1
        return res

    def run(t, S, budget, tag, with_true=True, goal=None):
        o, _ = lemmas.split(t)
        cand = cands[t]
        if goal is not None:
            if not hasattr(lp, 'goal_override'):
                lp.goal_override = {}
            lp.goal_override[t] = goal
        with lock:
            tl = [(lab, f) for f, lab in true[o].items()] if with_true else []
        lp.extra_axioms[t] = tl + [(x, cand[x]) for x in sorted(S)]
        with lock:
            hs = list(sketch[o])
        # sketch hints first: hints_for keeps the pool's order and a cap applies to the tail
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        if tag == 'final':
            lp.capture_given.add(t)
        # (23 Nov) each run's printed proof as DIR/proofs/<t>.<tag> (.weak for a weakened goal): sketch proofs are kept
        # as data, and none overwrites the final run's real proof (a target's runs are sequential in one thread)
        if not hasattr(lp, 'proof_name'):
            lp.proof_name = {}
        lp.proof_name[t] = f'{t}.{tag}' + ('.weak' if goal is not None else '')
        try:
            n, ok, dt, stats, res = lp.run_one(t, hints, 1, budget, False,
                                               c.final_cpu if tag == 'final' and c.final_cpu else a_cpu(budget))
        finally:
            lp.proof_name.pop(t, None)
        lp.extra_axioms.pop(t, None)
        if tag == 'final':
            # the final run's given rules, failed or not: which sketch steps the real theory derives
            # (realization labels of the moves, latticedata.py)
            lp.capture_given.discard(t)
            G_ = lp.captured.pop(t, [])
            d_ = os.path.join(c.dir, 'realized'); os.makedirs(d_, exist_ok=True)
            with open(os.path.join(d_, t), 'w') as f_:
                f_.write(f'# ok={int(ok)} sketch_hints={len(hs)}\n')
                f_.writelines(f'{l}\t{r}\n' for l, r in G_)
        if goal is not None:
            lp.goal_override.pop(t, None)
            if ok:   # (a proof of an instance is not one of T)
                with lock:
                    out.write(f'{t}\t{tag}:weak\t{len(S)}\tTHM\t-\t{dt:.2f}\t{goal[:120]}\n'); out.flush()
        used = lp.used.pop(t, set()) if ok else set()
        if ok:
            # (24 Nov, exp75) columns 4 and 5: each assume_* label's source goal at this run (csrc; assume_goal_J: the
            # original's goal J; '-' for a theory conjecture), and 1 for a proof of a weakened goal (a sketch with
            # goal= in its header): kNN labels are rewritten as the list changes, so assume.tsv alone cannot say which
            # goal a proof assumed, and a weakened goal's proof is not one of the target
            ou_ = t.rsplit('__goal_', 1)[0]
            su_ = ','.join(f'{x}=' + (csrc.get((t, x)) or (f'{ou_}__goal_{x[12:]}' if x.startswith('assume_goal_') else '-'))
                           for x in sorted(used) if x.startswith('assume_'))
            with lock:
                fu.write(f'{t}\t{tag}\t{",".join(sorted(used))}\t{su_}\t{int(goal is not None)}\n'); fu.flush()
        deps = lp.assumed.pop(t, [])
        U = {x for x in used if x.startswith('assume_')}
        ut = sorted(x for x in used if x.startswith('true_'))
        nt = len(ut)
        if ok and goal is None:
            last_true[t] = [tkey[(o, x)] for x in ut if (o, x) in tkey]
        if ok and res:
            with lock:
                for h in res:
                    if h not in seen[o]:
                        seen[o].add(h); sketch[o].append(h)
            if S or goal is not None:
                # each sketch proof's steps, for credit labels (which moves' hints a real proof reused)
                d_ = os.path.join(c.dir, 'sketches', t); os.makedirs(d_, exist_ok=True)
                with open(os.path.join(d_, tag), 'w') as f_:
                    f_.write(f'# S={",".join(sorted(S))}\n# U={",".join(sorted(U))}\n# goal={goal or ""}\n')
                    f_.writelines(f'{l}\t{r}\n' for l, r in res)
        with lock:
            out.write(f'{t}\t{tag}\t{len(S)}\t{"THM" if ok else "NO"}\t{len(U) if ok else -1}\t{dt:.2f}\t'
                      f'{",".join(short(x) for x in sorted(S))}\t{",".join(short(x) for x in sorted(U))}\t{len(hs)}\t{nt}\n')
            out.flush()
        js = {int(x.split('_')[2]) for x in S if x.startswith('assume_thy_')}
        if len(js) == 1 and goal is None and t in tmeta:   # (--theory-ts) a single-theory sketch: update its theory
            o_ = tmeta[t].get(js.pop())
            if o_:
                with lock:
                    thy_stats[o_][1] += 1
                    thy_stats[o_][0] += int(bool(ok and U and len(res) >= (c.min_sketch_steps or 30)))
        if ok and U and c.fill:
            fill(t, deps, tag)
        return ok, U, res, nt

    def fill(t, deps, tag):
        """Veroff's gap filling: prove the sketch proof's assumption-dependent lemmas without the
        assumptions (with the true lemmas so far and the sketch hints); the proven ones become
        true lemmas of the original."""
        o, _ = lemmas.split(t)
        if not deps:
            return
        path = os.path.join(lemmas.PROB, t + '.p')
        lines = [x for x in open(path) if x.startswith(('cnf(', 'fof(')) and 'conjecture' not in x]
        if (a.lemmas or a.lemma_knn) and lp.lemma_src:
            # the target's lemmas (proven siblings, kNN goals), as in its own runs
            if a.lemma_knn:
                txt, _ = lemmas.lemma_problem_knn(t, lp.lemma_src, a.lemmas, lp.lemma_index, a.lemma_knn, a.lemma_after)
            else:
                txt, _ = lemmas.lemma_problem(t, lp.lemma_src, a.lemmas, a.lemma_after)
            lines += [x + '\n' for x in txt.splitlines() if x.startswith('fof(lemma_')]
        with lock:
            tl = list(true[o].items())
            hs = list(sketch[o])
        lines += [f'fof({lab}, axiom, {f}).\n' for f, lab in tl]
        known = set()
        for x in lines:
            known.update(CONST.findall(x))
        with lock:
            todo = []
            for asm, (l, r) in deps:
                # (19 Nov 18:25) the goal's Skolem constants (x0, x1_2, ...) occur nowhere in this problem (its conjecture
                # is left out), so the step holds for all their values: generalise them to variables. Kept as constants,
                # 120 of the first 154 fill lemmas could match nothing (3 of them were ever used, against 22 of the 34
                # with variables only).
                cs = sorted(set(CONST.findall(l + ' ' + r)) - known)
                if cs:
                    ren_ = {cc: f'Yc{k}' for k, cc in enumerate(cs)}
                    rx_ = re.compile(r'\b(' + '|'.join(map(re.escape, cs)) + r')\b(?!\s*\()')
                    l = rx_.sub(lambda m: ren_[m.group(1)], l); r = rx_.sub(lambda m: ren_[m.group(1)], r)
                if l == r:
                    continue   # (a trivial step, e.g. true_2 of loops/SMK3: t = t)
                vs = sorted(set(VAR.findall(l + ' ' + r)) | set(re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', l + ' ' + r)))
                f = (f'! [{",".join(vs)}] : ' if vs else '') + f'{l} = {r}'
                if f in true[o] or f in checked[o]:
                    continue
                checked[o].add(f); todo.append((l, r, vs, f))
            todo = todo[:c.fill_max]
        if not todo:
            return
        for i, (l, r, vs, f) in enumerate(todo):
            sub = {v: f'skd{i}_{v.lower()}' for v in vs}
            g = lambda x: re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', lambda m: sub[m.group(0)], x)
            lines.append(f'cnf(dep_{i}, negated_conjecture, {g(l)} != {g(r)}).\n')
        tmp = os.path.join(c.dir, 'tmp', f'{t}.fill.p')
        with open(tmp, 'w') as fh:
            fh.writelines(lines)
        hints = hs + [h for h in lp.hints_for(t, pools, None) if h not in seen[o]]
        hp = tmp + '.hints'
        with open(hp, 'w') as fh:
            for h in hints:
                fh.write('\t'.join(h) + '\n')
        cmd = [a.twee, tmp, '--max-time', str(c.fill), '--no-colour', '--quiet', '--no-proof', '--print-hints',
               '--multi-goal', '--hints-file', hp, '--max-cpu', str(a_cpu(c.fill))] + a.args.split()
        if lp.model:
            m, v, gdir = lp.model
            cmd += ['--rule-model', m, '--rule-vocab', v, '--rule-goal', os.path.join(gdir, t)] + a.model_args.split()
        t0 = time.time()
        try:
            o_ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=c.fill * a.wall_factor + 30).stdout.decode('utf8', 'replace')
        except subprocess.TimeoutExpired as e:
            o_ = (e.stdout or b'').decode('utf8', 'replace')
        dt = time.time() - t0
        got = {line.split()[1] for line in o_.splitlines() if line.startswith('SOLVEDGOAL ')}
        ua = next((line.split()[1:] for line in o_.splitlines() if line.startswith('USEDAXIOMS')), None)
        if ua is None:
            ua = [m_.group(1) for m_ in (re.match(r'fof\(((?:lemma|true)_[^,]*),', x) for x in lines) if m_]
        prem = ','.join(sorted(x for x in ua if x.startswith(('lemma_', 'true_'))))
        new = []
        sig = lp.signature(t)
        with lock:
            for i, (l, r, vs, f) in enumerate(todo):
                ffa.write(f'{o}\t{f}\t{int(f"dep_{i}" in got)}\t{t}\t{tag}\n')
            ffa.flush()
            for i, (l, r, vs, f) in enumerate(todo):
                if f'dep_{i}' in got and f not in true[o] and len(true[o]) < c.true_max:
                    true[o][f] = f'true_{len(true[o])}'; new.append(f)
                    tkey[(o, true[o][f])] = loop.canon_key(l, r, sig)
                    ft.write(f'{o}\t{true[o][f]}\t{f}\t{tkey[(o, true[o][f])][0]}\t{tkey[(o, true[o][f])][1]}\t{t}\t{tag}\n')
                    ft.flush()
                    fpr.write(f'{o}\t{true[o][f]}\t{f}\t{t}\t{tag}\t{prem}\n'); fpr.flush()
            if got and 'HINTS-END' in o_:
                L, G = hintlib.extract_hints(o_)
                fh_ = []
                for l, r in L + G:
                    if 'skd' in l or 'skd' in r:
                        continue
                    k = loop.canon_key(l, r, sig)
                    if k[0] != k[1]:
                        fh_.append(k)
                    if k[0] != k[1] and k not in seen[o]:
                        seen[o].add(k); sketch[o].insert(0, k)   # real hints before the sketch's
                if fh_:
                    d_ = os.path.join(c.dir, 'fillhints', t); os.makedirs(d_, exist_ok=True)
                    with open(os.path.join(d_, tag), 'w') as f_:
                        f_.writelines(f'{x}\t{y}\n' for x, y in fh_)
            fo.write(f'{t}\t{tag}\t{len(deps)}\t{len(todo)}\t{len(got)}\t{len(new)}\t{len(true[o])}\t{dt:.2f}\n')
            fo.flush()
        for x in (tmp, hp):
            os.unlink(x)

    cap = c.max_sketch_time or 4 * c.sketch_time

    last_true = {}   # target -> the true lemmas its last proof used (canonical pairs)

    def a_cpu(b):
        return 10 * b

    tgroups = {}

    def nruns(t):
        """--final-only-ab: 0 sketch runs (the final only) on targets with bit 2 of crc32 set, else --runs"""
        if not c.final_only_ab:
            return c.runs
        import zlib
        return 0 if (zlib.crc32(t.encode()) >> 2) % 2 == 1 else c.runs   # by target: its own climb against its final alone

    def climb(t):
        cands[t] = candidates(t)
        with lock:
            o0_ = lemmas.split(t)[0]
            for x_, f_ in cands[t].items():
                src_ = csrc.get((t, x_)) or (f'{o0_}__goal_{x_[len("assume_goal_"):]}' if x_.startswith('assume_goal_') else '-')
                fa.write(f'{t}\t{getattr(c, "cprefix", {}).get(t, "")}\t{x_}\t{src_}\t{f_}\n')
            fa.flush()
        S0 = list(cands[t])
        queue = [frozenset(S0)] if S0 else []
        if tgroups.get(t):
            # one stronger theory (or generated equation) at a time (with the other assumptions, if any)
            other = frozenset(x for x in S0 if not x.startswith(('assume_thy_', 'assume_gen_')))
            queue = [g | other for g in tgroups[t]]
        tried = set(); runs = 0; real = None
        bt = c.sketch_time; anyproof = False
        banned = set(); minU = None; nt = 0
        while runs < nruns(t):
            if not queue and minU:
                # stuck at minU (no smaller set proves T): ban its assumptions and climb again from
                # the top without them, for proofs (and hints) that go another way
                banned |= minU; minU = None
                if tgroups.get(t):
                    other = frozenset(x for x in S0 if not x.startswith(('assume_thy_', 'assume_gen_')))
                    queue += [g2 for g2 in ((g | other) - banned for g in tgroups[t])
                              if g2 and g2 not in tried and any(x.startswith(('assume_thy_', 'assume_gen_')) for x in g2)]
                else:
                    rest = frozenset(S0) - banned
                    if rest and rest not in tried:
                        queue.append(rest)
            if not queue:
                break
            queue.sort(key=len)
            S = queue.pop(0)
            if S in tried:
                continue
            tried.add(S)
            ok, U, res, nt = run(t, S, bt, f'{getattr(c, "cprefix", {}).get(t, "")}s{runs}')
            runs += 1
            if ok and not U:
                real = res; break
            if ok and c.min_sketch_steps and len(res or ()) < c.min_sketch_steps:
                L = {u for u in U if u.startswith(('assume_law_', 'assume_thy_', 'assume_gen_'))}
                if L:
                    # (--min-sketch-steps) a law that makes the sketch trivial gives a dozen hints:
                    # ban the laws it used and start again from the top without them
                    banned |= L
                    if tgroups.get(t):   # one theory (generated equation) at a time, as at the start
                        other = frozenset(x for x in S0 if not x.startswith(('assume_thy_', 'assume_gen_')))
                        queue = [g2 for g2 in ((g | other) - banned for g in tgroups[t])
                                 if g2 and g2 not in tried and any(x.startswith(('assume_thy_', 'assume_gen_')) for x in g2)]
                    else:
                        rest = frozenset(S0) - banned
                        queue = [rest] if rest and rest not in tried else []
                    continue
            if not ok and not anyproof and tgroups.get(t) and queue:
                continue   # (--theories) the next theory first
            if not ok and not anyproof:
                # even the top of the lattice is too hard: retry it with twice the time, up to the cap
                if bt * 2 > cap:
                    break
                bt *= 2; tried.discard(S); queue.append(S)
            if ok:
                anyproof = True
                if minU is None or len(U) < len(minU):
                    minU = frozenset(U)
                # (laws first: they may be false; then the farthest siblings)
                for u in sorted(U, key=lambda x: (not x.startswith('assume_law_'),
                                                  -abs(int(x[12:]) - lemmas.split(t)[1]) if x.startswith('assume_goal_') else 0)):
                    queue.append(frozenset(U - {u}))
        if real is None:
            ok, U, res, nt = run(t, frozenset(), c.final_time, 'final')
            if ok:
                real = res
        direct = real is not None and not nt
        if real is not None and nt:
            # a proof with true lemmas (--fill): also try one without them, with all the hints
            ok, _, res, _ = run(t, frozenset(), c.final_time, 'direct', with_true=False)
            if ok:
                direct = True; real = res
        if real is not None:
            with lock:
                sf.write(f'{t}\t1\t0\n'); sf.flush()
                if not direct:
                    out.write(f'{t}\tchain\t0\tTHM\t0\t0\t\t\t0\t{nt}\n'); out.flush()
                with open(os.path.join(c.dir, 'hints', t), 'w') as hf:
                    # (a chain proof: the true lemmas it used are hints too)
                    for l, r in list(real) + ([] if direct else [k for k in last_true.get(t, []) if k not in real]):
                        hf.write(f'{l}\t{r}\n')
        return t, real is not None, runs

    def weakenings(t):
        """(--updown) weaker goals: instances of T's unit conjecture, two variables merged (milder)
        first, then one variable set to the unit e."""
        try:
            lits = hintsel.goal_lits(t)
        except Exception:
            return []
        if len(lits) != 1 or not lits[0][0]:
            return []
        _, l, r = lits[0]
        vs = sorted(set(VAR.findall(l + ' ' + r)), key=lambda v: int(v[1:]))
        def inst(sub):
            f = lambda x: VAR.sub(lambda m: sub.get(m.group(0), m.group(0)), x)
            l2, r2 = f(l), f(r)
            ws = sorted(set(VAR.findall(l2 + ' ' + r2)), key=lambda v: int(v[1:]))
            return ''.join(f'! [{w}] : ' for w in ws) + f'{l2} = {r2}'
        out = [inst({w: v}) for i, v in enumerate(vs) for w in vs[i + 1:]]
        out += [inst({v: 'e'}) for v in vs]
        return list(dict.fromkeys(out))

    policy = None
    def move_arm(t):
        """--move-ab: the targets that use the policy (odd crc32 of the original's name); the others the fixed order"""
        import zlib   # (by the original: its goals' proofs come in chains, so the unit is the original)
        return zlib.crc32(lemmas.split(t)[0].encode()) % 2 == 1
    if c.move_model:
        import json, math, random, latticedata, latticepolicy
        policy = json.load(open(c.move_model))

    def climb2(t):
        """(--updown, user 15 Nov; Hernandez-Korovin IJCAR 2018 over-approximation) start at each
        stronger theory (or generated equation); when none proves T, go up: unions of the theories and
        weaker goals (instances), alone and in the first theory. From every proof go down: drop a used
        assumption, or restore the goal. Every proof's steps become hints of the original."""
        cands[t] = candidates(t)
        with lock:
            o0_ = lemmas.split(t)[0]
            for x_, f_ in cands[t].items():
                src_ = csrc.get((t, x_)) or (f'{o0_}__goal_{x_[len("assume_goal_"):]}' if x_.startswith('assume_goal_') else '-')
                fa.write(f'{t}\t{getattr(c, "cprefix", {}).get(t, "")}\t{x_}\t{src_}\t{f_}\n')
            fa.flush()
        S0 = frozenset(cands[t])
        groups = tgroups.get(t) or ([S0] if S0 else [])
        other = frozenset(x for x in S0 if not x.startswith(('assume_thy_', 'assume_gen_')))
        queue = [(g | other, None) for g in groups] or [(frozenset(), None)]
        tried = set(); runs = 0; real = None; anyproof = False; banned = set(); up_level = 0
        PRE = ('assume_law_', 'assume_thy_', 'assume_gen_')
        failed = []   # sets that failed on the real goal at the current level (for --up-single)

        def single_key(x):
            m_ = re.match(r'assume_thy_(\d+)_(lem)?(\d+)$', x)
            if m_:
                return (1 if m_.group(2) else 0, int(m_.group(1)), int(m_.group(3)))
            return (2 if x.startswith('assume_law_') else 3, 0, 0)
        singles = sorted((x for x in S0 if x.startswith(PRE)), key=single_key)
        while runs < nruns(t):
            if not queue:
                if anyproof or up_level >= (c.up_levels if c.up_single else 1):
                    break
                up_level += 1
                frontier, failed = failed, []
                if c.up_single:
                    # one more axiom: the best failed sets of the level below, each with one more
                    # assumption (another theory's axiom, a stronger theory's lemma, a law), in rank order
                    for S_ in frontier[:c.up_beam]:
                        n_ = 0
                        for x in singles:
                            if x in S_ or x in banned:
                                continue
                            queue.append((S_ | {x}, None)); n_ += 1
                            if n_ >= c.up_width:
                                break
                if up_level > 1:
                    continue
                if len(groups) >= 2:
                    queue.append((groups[0] | groups[1] | other, None))
                if len(groups) >= 3:
                    queue.append((groups[0] | groups[1] | groups[2] | other, None))
                for gv in weakenings(t)[:c.weaken]:
                    queue.append((other, gv))
                    if groups:
                        queue.append((groups[0] | other, gv))
                continue
            if policy is None or (c.move_ab and not move_arm(t)):
                queue.sort(key=lambda n: (n[1] is not None, len(n[0])))
                S, g = queue.pop(0)
            else:
                # (--move-model) the learned policy: softmax over the moves' scores, some random moves
                if random.random() < c.move_eps:
                    i_ = random.randrange(len(queue))
                else:
                    sc = [latticepolicy.score(policy, [latticedata.move_features(t, sorted(n[0] - banned), n[1], runs)[k]
                                                        for k in policy['features']]) / c.move_temp for n in queue]
                    mx = max(sc); ws = [math.exp(x - mx) for x in sc]
                    i_ = random.choices(range(len(queue)), weights=ws)[0]
                S, g = queue.pop(i_)
            S = frozenset(S) - banned
            if (S, g) in tried or (not S and g is None):
                continue
            tried.add((S, g))
            ok, U, res, nt = run(t, S, c.sketch_time, f'{getattr(c, "cprefix", {}).get(t, "")}s{runs}', goal=g)
            runs += 1
            if not ok and g is None:
                failed.append(S)
            if ok and not U and g is None:
                real = res; break
            if ok and U and c.min_sketch_steps and len(res or ()) < c.min_sketch_steps:
                banned |= {u for u in U if u.startswith(PRE)}
                if not any(x.startswith(PRE) for x in U - banned):
                    continue
            if ok:
                anyproof = True
                U = frozenset(U)
                for u in U:
                    queue.append((U - {u}, g))
                if g is not None:
                    queue.append((U, None))
        if real is None:
            ok, U, res, nt = run(t, frozenset(), c.final_time, 'final')
            if ok:
                real = res
        direct = real is not None and not nt
        if real is not None and nt:
            ok, _, res, _ = run(t, frozenset(), c.final_time, 'direct', with_true=False)
            if ok:
                direct = True; real = res
        if real is not None:
            with lock:
                sf.write(f'{t}\t1\t0\n'); sf.flush()
                if not direct:
                    out.write(f'{t}\tchain\t0\tTHM\t0\t0\t\t\t0\t{nt}\n'); out.flush()
                with open(os.path.join(c.dir, 'hints', t), 'w') as hf:
                    for l, r in list(real) + ([] if direct else [k for k in last_true.get(t, []) if k not in real]):
                        hf.write(f'{l}\t{r}\n')
                if c.chain:
                    # (--chain) the proof feeds the original's later targets at once: a sibling lemma,
                    # and its steps as hints (the online loop's chain, inside the climb)
                    o, k = lemmas.split(t)
                    lp.solved[t] = (1, 0.0)
                    lp.lemma_src.setdefault(o, set()).add(k)
                    for h in real:
                        if h not in seen[o]:
                            seen[o].add(h); sketch[o].insert(0, h)
        return t, real is not None, runs

    if c.updown:
        climb = climb2

    if c.live:
        live(c, a, lp, gl, pools, ix, climb, out, lock)
        return
    todo = [n for n in lp.names if n not in lp.solved]
    if c.targets:
        keep = {l.split()[0] for l in open(c.targets) if l.strip()}
        todo = [n for n in todo if n in keep]
        print(f'--targets: {len(todo)} of {len(keep)} listed goals unsolved here', flush=True)
    t0 = time.time(); nsolved = 0
    with ThreadPoolExecutor(c.j) as ex:
        for t, ok, runs in ex.map(climb, todo):
            nsolved += ok
            print(f'{t} {"THM" if ok else "NO"} sketch-runs={runs} total={nsolved} {time.time()-t0:.0f}s', flush=True)
    print(f'climb: {nsolved}/{len(todo)} {time.time()-t0:.0f}s', flush=True)


def live(c, a, lp, gl, pools, ix, climb, out, lock):
    """--live: climb the stalled goals of the running loop c.live, as they come."""
    import glob
    from concurrent.futures import wait, FIRST_COMPLETED
    D = c.live
    skip = set()
    for f in filter(None, c.exclude.split(',')):
        skip |= {l.strip() for l in open(f) if l.strip()}
    out.flush()
    climbed = {l.split('\t')[0] for l in open(os.path.join(c.dir, 'climb.tsv'))}
    nclimb = collections.Counter(l.split('\t')[0] for l in open(os.path.join(c.dir, 'climb.tsv'))
                                 if l.split('\t')[1:2] == ['final'])
    at_climb = {}    # head -> its original's number of proven goals at its last climb (--reclimb-heads)
    RECL = [l.split()[0] for l in open(c.reclimb) if l.strip()] if c.reclimb else []   # (--reclimb)
    c.cprefix = {}   # target -> run tag prefix of a re-climb (r1, r2, ...), so its sketch logs stay apart
    def dst():
        S, R = set(), 0
        for l in open(os.path.join(D, 'solved.tsv')):
            w = l.split('\t')
            if len(w) >= 2 and l.endswith('\n'):
                S.add(w[0]); R = max(R, int(w[1]))
        return S, R
    def stalled(S, busy):
        rfs = sorted(glob.glob(os.path.join(D, 'r*', 'results.tsv')), key=lambda p: int(p.split('/')[-2][1:]))
        last, fresh = {}, set()
        for l in open(rfs[-1]):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5:
                last[w[0]] = (w[1], w[4])
                if w[4] == 'L0':
                    fresh.add(w[0])
        by = lemmas.by_original(S)
        def dist(n):   # proof lines to the nearest proven goal below
            o, k = lemmas.split(n)
            below = [j for j in by.get(o, ()) if j < k and f'{o}__goal_{j}' in gl]
            return gl[n] - gl[f'{o}__goal_{max(below)}'] if below and n in gl else 10 ** 6
        # (only after a fresh run in the latest round failed too: fresh 20 s in the current context
        # proved 36/95 of the climber's first targets at 49 proofs/CPU-h, the climber 31/102 at 15)
        res = [n for n, (ok, lev) in last.items() if ok == 'NO' and lev != 'L0' and n in fresh and n not in S
               and n not in climbed and n not in skip and n not in busy]
        res.sort(key=lambda n: (dist(n), n))
        if RECL:   # (--reclimb) after the new targets
            rs = set(res)
            res += sorted((n for n in RECL if n not in S and n not in skip and n not in busy and n not in rs
                           and nclimb[n] < c.reclimb_max), key=lambda n: (dist(n), n))
        if not c.reclimb_heads:
            return res
        # (--reclimb-heads N) each original's first unsolved goal, climbed up to N times (the climbs are randomized
        # by the move policy and theory sampling; a head's proof opens its original's later goals), fewest climbs
        # first; interleaved with the new targets
        first = {}
        for n in gl:
            if n in S or n in skip or n in busy:
                continue
            o, k = lemmas.split(n)
            if o not in first or k < first[o][0]:
                first[o] = (k, n)
        # a climbed head again only when its original has new proofs since that climb (new lemmas and hints):
        # re-climbs in an unchanged context gave 2 proofs in 87 climbs (0.45 per CPU h, new targets 2.1)
        def ok_head(n):
            if nclimb[n] == 0:
                return True
            o = lemmas.split(n)[0]
            at_climb.setdefault(n, len(by.get(o, ())))
            return nclimb[n] < c.reclimb_heads and len(by.get(o, ())) > at_climb[n]
        heads = sorted((n for _, n in first.values() if ok_head(n)), key=lambda n: (nclimb[n], dist(n), n))
        if c.heads_only:   # (--heads-only) only the heads: new ones, and climbed ones whose original changed
            return heads
        hs = set(heads); res = [n for n in res if n not in hs]
        mixed = []
        while heads or res:
            if heads:
                mixed.append(heads.pop(0))
            if res:
                mixed.append(res.pop(0))
        return mixed
    def refresh(S):
        # (24 Nov) under the lock: a worker's --chain proof adds to lp.solved (under the lock) while build_pools
        # iterates it ("dictionary changed size during iteration" ended CLQ83 at 16:03)
        with lock:
            new = [n for n in S if n not in lp.solved]
            for n in new:
                lp.solved[n] = (0, 0.0)
            if new:
                t1 = time.time()
                pools.clear(); pools.update(lp.build_pools())
                lp.lemma_src = {o: set(v) for o, v in lemmas.by_original(lp.solved).items()}
                if a.lemma_knn:
                    lp.lemma_index = lemmas.LemmaIndex(sorted(lp.solved), subsets=a.lemma_subsets)
                if c.knn:
                    ix['u'] = lemmas.LemmaIndex(sorted(n for n in gl if n not in lp.solved), subsets=True)
                print(f'live: refreshed with {len(new)} new proofs of {D} in {time.time()-t1:.0f}s', flush=True)
    def others():
        """twee processes of this user that are not this climber's"""
        n = 0
        for pid in os.listdir('/proc'):
            if not pid.isdigit():
                continue
            try:
                with open(f'/proc/{pid}/cmdline', 'rb') as f:
                    argv = f.read().split(b'\0')
            except OSError:
                continue
            if argv and os.path.basename(argv[0]).startswith(b'twee') and len(argv) > 1 \
                    and not argv[1].startswith(c.dir.encode()):
                n += 1
        return n
    t0 = time.time(); nsolved = 0; last_refresh = time.time()
    with ThreadPoolExecutor(c.j) as ex:
        running = {}
        while True:
            S, R = dst()
            if time.time() - last_refresh >= c.refresh:
                refresh(S); last_refresh = time.time()
            busy = set(running.values())
            todo = stalled(S, busy)
            cap = c.j if not c.cpus else max(1, min(c.j, c.cpus - others()))
            while len(running) < cap and todo:
                t = todo.pop(0)
                if nclimb[t]:
                    c.cprefix[t] = f'r{nclimb[t]}'
                running[ex.submit(climb, t)] = t
            if not running:
                time.sleep(60); continue
            fin, _ = wait(list(running), timeout=30, return_when=FIRST_COMPLETED)
            for f in fin:
                t = running.pop(f)
                try:
                    t, ok, runs = f.result()
                except Exception:   # (one climb's error must not stop the live climber)
                    import traceback
                    print(f'{t} ERROR {traceback.format_exc()}', flush=True)
                    climbed.add(t)
                    continue
                climbed.add(t); nclimb[t] += 1
                S, R = dst()
                at_climb[t] = len(lemmas.by_original(S).get(lemmas.split(t)[0], ()))
                if ok and t not in S:
                    # (the hints file is already in place: DIR/hints links to D/hints)
                    with open(os.path.join(D, 'solved.tsv'), 'a') as sf:
                        sf.write(f'{t}\t{R}\t0\n')
                    nsolved += 1
                print(f'{t} {"THM" if ok else "NO"} sketch-runs={runs} total={nsolved} '
                      f'{time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
