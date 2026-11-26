"""condprove.py OUT [--set sets/all] [--trusted T.trusted] [-j 6] [--time 5] [--sibs 10] [--knn 30] [--only GOALS]

(23 Nov) Conditional proofs of the unsolved goals: each unsolved goal of SET (not in TRUSTED) with its SIBS nearest
earlier goals of its original as axioms (lemma_goal_J), proved or not (AIM60k's goals are steps of Prover9's proofs,
so they are true), and the KNN nearest trusted goals (lemma_knn_I_<goal>). One plain twee-pg61 run of TIME abstract
seconds (--abstract-time 2000, no rule model, no hints), --no-proof --quiet; a proved run is rerun with the proof
printed into OUT/proofs/<goal> (the used axioms come from it).

OUT/results.tsv: goal, THM/NO, seconds, used lemma_goal_J that are unproved (comma list, '-' if none), used ones
that are proved, the number of used kNN lemmas. A THM row with no unproved sibling used is an unconditional proof;
it is NOT entered anywhere (OUT is outside loops/, so no loop, proofq, trust.py or the packer sees it).

Write OUT outside /project/hintwork/loops."""
import os, sys, re, subprocess, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import lemmas, hintsel
a = sys.argv[1:]
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
SET = opt('--set', '/project/hintwork/sets/all'); TR = opt('--trusted', '/project/hintwork/loops/TRUSTNOW/t2139.trusted')
J = int(opt('-j', '6')); TM = opt('--time', '5'); SIBS = int(opt('--sibs', '10')); KNN = int(opt('--knn', '30'))
# (24 Nov, exp82) --knn-skip S: the kNN lemmas ranked S..S+KNN-1 (a disjoint slice of the ranking)
KSKIP = int(opt('--knn-skip', '0'))
ONLY = opt('--only', ''); TWEE = '/project/bin/twee-pg61'
# (23 Nov) --twee PATH: another binary (e.g. /project/bin/twee-e63 with --args --lazy-lemmas)
TWEE = opt('--twee', TWEE)
# (23 Nov, the step test bed) --after N: also the N nearest later siblings (any status; true as well); --args: more
# twee flags; --all: every goal of --only, solved or not
AFTER = int(opt('--after', '0')); XARGS = opt('--args', '').split(); ALL = '--all' in a
# --proved: siblings (earlier and --after later) only from TRUSTED, so every proof is a real one (no assumption)
PROVED = '--proved' in a
# --prev DIR (a sweep before this one): a goal whose problem text is the same as in DIR and failed there is not run
# again (twee is deterministic); its row is written with status SAME. (24 Nov) DIR,DIR...: the first dir that has the
# goal decides (e.g. plainlive's last H cycle, then the HLW1 sweep, when H moves to the local heads)
PREV = opt('--prev', '')
PREVS = [x for x in PREV.split(',') if x]
# (24 Nov) --prev-ignore-knn: compare the problems without their lemma_knn_* lines, so a goal is rerun only when its
# axioms or sibling lemmas changed (a newly proved sibling), not when its kNN list moved (plainlive's local heads)
PIK = '--prev-ignore-knn' in a
def _pk(x):
    return ''.join(l for l in x.splitlines(True) if not l.startswith('fof(lemma_knn_')) if PIK else x
# (23 Nov, the hint bed) --hints-lemmas CAP: also the hints of the problem's lemma goals (their proofs' steps,
# /project/hintwork/loops/UL/hints/<goal>), the siblings nearest first, then the kNN lemmas by rank, at most CAP, as
# twee's --hints-file OUT/h/<goal>.hints (default factor); the problem text stays as without
HCAP = int(opt('--hints-lemmas', '0')); HDIR = opt('--hints-dir', '/project/hintwork/loops/UL/hints')
# (26 Nov, exp92) --listen K: each run also listens to up to K unsolved plain goals of its original (hintsel.listen_clauses,
# as loop.py --listen; twee-e61m, whose search is the same with and without them and, without them, the same as
# twee-e61's). A listened goal X proved there gets a run of its own problem: the run's text (the original's axioms and
# the run's lemmas, all trusted under --proved) with the run's conjecture line replaced by X's; its row is written like
# any other (THM or NO), so condimport.py reruns p/<X>.p as usual. OUT/listened.tsv: X, the run's goal, THM/NO.
# --prev compares the problems without the listened lines (they are not in p/<goal>.p)
LISTEN = int(opt('--listen', '0'))
# (26 Nov, exp94) --equation: a conditional goal whose hypothesis has a variable side (t = X) runs as its equivalent
# equation C[X := t] (lemmas.equation_problem, the one-point rule) in place of its conjecture line; other goals as
# before. condimport.py reruns p/<goal>.p, so an imported proof is of that equation
EQN = '--equation' in a
if LISTEN:
    if TWEE == '/project/bin/twee-pg61':
        TWEE = '/project/bin/twee-e61m'   # (twee-pg61 adds $TWEE_PG_ARGS, unset in plainlive's runs)
    assert 'e61m' in TWEE, f'--listen needs twee-e61m, not {TWEE}'
    assert not HCAP, '--listen with --hints-lemmas: the listened goal would need the run hints file'
a = [x for x in a if x not in ('--all', '--proved', '--prev-ignore-knn', '--equation')]
OUT = os.path.abspath(a[0])
assert not OUT.startswith('/project/hintwork/loops'), 'OUT must be outside loops/'
os.makedirs(f'{OUT}/p', exist_ok=True); os.makedirs(f'{OUT}/proofs', exist_ok=True)
G = [l.strip() for l in open(SET) if l.strip()]
T = {l.split()[0] for l in open(TR) if l.strip()}
U = [g for g in G if g not in T or ALL]
if ONLY:
    keep = {l.strip() for l in open(ONLY) if l.strip()}; U = [g for g in U if g in keep]
done = set()
RES = f'{OUT}/results.tsv'
if os.path.exists(RES):
    done = {l.split('\t')[0] for l in open(RES) if l.strip()}
U = [g for g in U if g not in done]
allg = collections.defaultdict(set)
for x in G:
    if not PROVED or x in T:
        o, k = lemmas.split(x); allg[o].add(int(k))
prevno, prevdir = {}, {}
for d_ in PREVS:
    for l in open(f'{d_}/results.tsv'):
        if l.strip() and l.split('\t')[0] not in prevno:
            prevno[l.split('\t')[0]] = l.split('\t')[1] in ('NO', 'SAME'); prevdir[l.split('\t')[0]] = d_
t_ = time.time()
index = lemmas.LemmaIndex(sorted(T), subsets=True) if KNN else None
# (23 Nov) --index kd|kp: loop.py's other kNN selections (start_vix): kd adds MaSh-style proof dependencies (the
# steps of the nearest proven goals' proofs, HDIR, weight 1, 50 nearest), kp weights similarity by lemma use counts
# (USEDAXIOMS of production's kept outputs, pop 0.3)
IX = opt('--index', '')
if IX == 'kd' and index:
    index.deps, index.dep_idf = lemmas.proof_deps(HDIR, sorted(T)); index.dep_w = 1.0
    index.dep_n = max(50, KNN)   # (09:00) dep_n 50 left 203 of 400 kNN lemmas: kd re-ranks only its dep_n nearest and their deps
elif IX == 'kp' and index:
    index.uses = lemmas.lemma_uses(['/project/hintwork/loops/UL']); index.pop = 0.3
elif IX.startswith('learned:') and index:
    # (23 Nov, notes/2026-11-23-lemma-ranker.md) exp/lemmarank.py's model re-ranks the similarity list's top 2,000
    # (needs lightgbm: run under /project/hintwork/venv/bin/python3)
    sys.path.insert(0, '/project/twee/hints/exp')
    import lemmarank
    # (23 Nov) --rank-loop DIR: the ranker's use counts, proof steps and hints dir from loop DIR (its kept
    # outputs and DIR/hints) instead of production's, so a test in another loop's context (e.g. Z9's) does not see
    # production's proofs
    RL = opt('--rank-loop', '')
    if RL:
        ctx_ = lemmarank.Ctx(parts=(index, lemmas.lemma_uses([RL]), lemmas.proof_deps(f'{RL}/hints', sorted(T))[0],
                                    f'{RL}/hints'))
        ctx_.used_by()
        index = lemmarank.Ranker(IX.split(':', 1)[1], ctx=ctx_)
    else:
        index = lemmarank.Ranker(IX.split(':', 1)[1], TR)
    index.POOL = int(opt('--rank-pool', '2000'))   # (23 Nov) loop.py --lemma-ranker-all's pool: 1,000
    index.MIX = int(opt('--rank-mix', '0'))        # (23 Nov) the similarity list's top N first, then the model's
elif IX:
    sys.exit(f'--index {IX}: kd, kp or learned:MODEL')
print(f'condprove: {len(U)} unsolved goals to run ({len(done)} done), index {time.time()-t_:.0f}s', flush=True)
import threading
LOCK = threading.Lock(); STARTED, CRED = set(), set()
UNS = collections.defaultdict(list)   # (--listen) original -> its unsolved goals
for x in G:
    if x not in T:
        UNS[lemmas.split(x)[0]].append(x)
CONJ = re.compile(r'fof\(\s*[^,\s]+\s*,\s*conjecture\s*,')
def listen_one(g, x, txt):
    """(--listen) X, proved as a listened goal in G's run: a run of G's problem with X's conjecture; its results row"""
    with LOCK:
        if x in STARTED or x in CRED or x in done or x in T:
            return ''
        CRED.add(x)
    cl = [l for l in txt.splitlines(True) if CONJ.match(l)]
    xl = [l for l in open(os.path.join(lemmas.PROB, x + '.p')) if CONJ.match(l)]
    if len(cl) != 1 or len(xl) != 1:
        return ''
    tx = txt.replace(cl[0], xl[0].rstrip('\n') + '\n')
    px = f'{OUT}/p/{x}.p'
    open(px, 'w').write(tx)
    t0 = time.time()
    try:
        r = subprocess.run([TWEE, px] + base + ['--quiet', '--no-proof'], capture_output=True, text=True,
                           timeout=max(600, 10 * float(TM)))
    except subprocess.TimeoutExpired:
        return f'{x}\tTIMEOUT\t{time.time() - t0:.2f}\t-\t-\t0\n'
    line = finish(x, px, r.stdout, time.time() - t0, [])
    with open(f'{OUT}/listened.tsv', 'a') as f:
        f.write(f'{x}\t{g}\t{line.split(chr(9))[1]}\n')
    return line
base = ['--max-time', TM, '--abstract-time', '2000', '--no-colour', '--no-resume-requeue', '--no-eqhint-consider'] + XARGS
AX = re.compile(r'^Axiom \d+ \(([^)]*)\)')
def one(g):
    o, k = lemmas.split(g)
    with LOCK:
        if g in CRED:   # (--listen) its row came from a listened proof in another run of this sweep
            return ''
        STARTED.add(g)
    if index:
        txt, _ = lemmas.lemma_problem_knn(g, allg, SIBS, index, KNN, skip=KSKIP)
    else:
        txt, _ = lemmas.lemma_problem(g, allg, SIBS)
    if AFTER:
        up = sorted(j for j in allg[o] if j > int(k))[:AFTER]
        for j in up:
            f_ = lemmas.lemma_form(f'{o}__goal_{j}') or (lemmas.HORN and lemmas.conjecture(f'{o}__goal_{j}'))  # (exp82) Horn
            if f_:
                txt += f'fof(lemma_goal_{j},axiom,{f_}).\n'
    if EQN:
        txt = lemmas.equation_problem(g, txt)
    p = f'{OUT}/p/{g}.p'
    open(p, 'w').write(txt)
    if prevno.get(g) and os.path.exists(f'{prevdir[g]}/p/{g}.p') and _pk(open(f'{prevdir[g]}/p/{g}.p').read()) == _pk(txt):
        return f'{g}\tSAME\t0.00\t-\t-\t0\n'
    hx = []
    if HCAP:
        names = re.findall(r'fof\((lemma_\w+),axiom,', txt)
        sib = sorted((n_ for n_ in names if n_.startswith('lemma_goal_')), key=lambda n_: abs(int(n_[11:]) - int(k)))
        kn = sorted((n_ for n_ in names if n_.startswith('lemma_knn_')), key=lambda n_: int(n_.split('_')[2]))
        seen, hs = set(), []
        for n_ in sib + kn:
            src = f'{o}__goal_{n_[11:]}' if n_.startswith('lemma_goal_') else n_.split('_', 3)[3]
            try:
                for l in open(f'{HDIR}/{src}'):
                    w = l.rstrip('\n').split('\t')
                    if len(w) >= 2 and (w[0], w[1]) not in seen:
                        seen.add((w[0], w[1])); hs.append(f'{w[0]}\t{w[1]}\n')
            except OSError:
                pass
            if len(hs) >= HCAP:
                break
        os.makedirs(f'{OUT}/h', exist_ok=True)
        hp = f'{OUT}/h/{g}.hints'; open(hp, 'w').write(''.join(hs[:HCAP])); hx = ['--hints-file', hp]
    lg = hintsel.listen_clauses(g, UNS.get(o, ()), LISTEN, 100000) if LISTEN else []
    rp = p
    if lg:
        rp = f'{OUT}/p/{g}.l.p'
        open(rp, 'w').write(txt + ''.join(lg))
    t0 = time.time()
    try:
        # (24 Nov) the wall cap 10 x --time (at least 600 s): a flat 600 s stopped exp74's 1200 abstract s runs at about
        # a third of their time
        r = subprocess.run([TWEE, rp] + base + hx + ['--quiet', '--no-proof'], capture_output=True, text=True,
                           timeout=max(600, 10 * float(TM)))
    except subprocess.TimeoutExpired:
        # (23 Nov) --backwards-goal 2 ran past the abstract-time limit (10 minutes, 5.8 GB): a row, not a crash
        return f'{g}\tTIMEOUT\t{time.time() - t0:.2f}\t-\t-\t0\n'
    finally:
        if rp != p and os.path.exists(rp):
            os.unlink(rp)
    dt = time.time() - t0
    line = finish(g, p, r.stdout, dt, hx)
    for x in (l.split()[1][len('listen_'):] for l in r.stdout.splitlines() if l.startswith('SOLVEDGOAL listen_')):
        line += listen_one(g, x, txt)
    return line
def finish(g, p, stdout, dt, hx):
    """a run's results row (a proved run is rerun with the proof printed into OUT/proofs/<goal>)"""
    o = lemmas.split(g)[0]
    ok = 'RESULT: Theorem' in stdout
    unp, pro, nk = '-', '-', 0
    if ok:
        r2 = subprocess.run([TWEE, p] + base + hx, capture_output=True, text=True, timeout=max(600, 10 * float(TM)))
        open(f'{OUT}/proofs/{g}', 'w').write(r2.stdout)
        used = [m[1] for l in r2.stdout.splitlines() for m in [AX.match(l)] if m]
        sib = [int(x[len('lemma_goal_'):]) for x in used if x.startswith('lemma_goal_')]
        nk = sum(1 for x in used if x.startswith('lemma_knn_'))
        u_ = [j for j in sib if f'{o}__goal_{j}' not in T]; p_ = [j for j in sib if f'{o}__goal_{j}' in T]
        unp = ','.join(map(str, sorted(u_))) or '-'; pro = ','.join(map(str, sorted(p_))) or '-'
    return f'{g}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{unp}\t{pro}\t{nk}\n'
n = 0; th = 0
with open(RES, 'a') as fo, ThreadPoolExecutor(J) as ex:
    for out_ in ex.map(one, U):
        for line in out_.splitlines(True):   # (--listen: a run's row plus its listened goals' rows; none if credited)
            fo.write(line); fo.flush(); n += 1; th += line.split('\t')[1] == 'THM'
        if n % 200 == 0:
            print(f'condprove: {n}/{len(U)} THM {th} {time.strftime("%H:%M:%S")}', flush=True)
print(f'condprove: done {n} THM {th} {time.strftime("%H:%M:%S")}', flush=True)
