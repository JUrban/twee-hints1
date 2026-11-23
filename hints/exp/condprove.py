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
import lemmas
a = sys.argv[1:]
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
SET = opt('--set', '/project/hintwork/sets/all'); TR = opt('--trusted', '/project/hintwork/loops/TRUSTNOW/t2139.trusted')
J = int(opt('-j', '6')); TM = opt('--time', '5'); SIBS = int(opt('--sibs', '10')); KNN = int(opt('--knn', '30'))
ONLY = opt('--only', ''); TWEE = '/project/bin/twee-pg61'
# (23 Nov) --twee PATH: another binary (e.g. /project/bin/twee-e63 with --args --lazy-lemmas)
TWEE = opt('--twee', TWEE)
# (23 Nov, the step test bed) --after N: also the N nearest later siblings (any status; true as well); --args: more
# twee flags; --all: every goal of --only, solved or not
AFTER = int(opt('--after', '0')); XARGS = opt('--args', '').split(); ALL = '--all' in a
# --proved: siblings (earlier and --after later) only from TRUSTED, so every proof is a real one (no assumption)
PROVED = '--proved' in a
# --prev DIR (a sweep before this one): a goal whose problem text is the same as in DIR and failed there is not run
# again (twee is deterministic); its row is written with status SAME
PREV = opt('--prev', '')
# (23 Nov, the hint bed) --hints-lemmas CAP: also the hints of the problem's lemma goals (their proofs' steps,
# /project/hintwork/loops/UL/hints/<goal>), the siblings nearest first, then the kNN lemmas by rank, at most CAP, as
# twee's --hints-file OUT/h/<goal>.hints (default factor); the problem text stays as without
HCAP = int(opt('--hints-lemmas', '0')); HDIR = opt('--hints-dir', '/project/hintwork/loops/UL/hints')
a = [x for x in a if x not in ('--all', '--proved')]
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
prevno = {}
if PREV:
    prevno = {l.split('\t')[0]: l.split('\t')[1] in ('NO', 'SAME') for l in open(f'{PREV}/results.tsv') if l.strip()}
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
base = ['--max-time', TM, '--abstract-time', '2000', '--no-colour', '--no-resume-requeue', '--no-eqhint-consider'] + XARGS
AX = re.compile(r'^Axiom \d+ \(([^)]*)\)')
def one(g):
    o, k = lemmas.split(g)
    if index:
        txt, _ = lemmas.lemma_problem_knn(g, allg, SIBS, index, KNN)
    else:
        txt, _ = lemmas.lemma_problem(g, allg, SIBS)
    if AFTER:
        up = sorted(j for j in allg[o] if j > int(k))[:AFTER]
        for j in up:
            f_ = lemmas.lemma_form(f'{o}__goal_{j}')
            if f_:
                txt += f'fof(lemma_goal_{j},axiom,{f_}).\n'
    p = f'{OUT}/p/{g}.p'
    open(p, 'w').write(txt)
    if PREV and prevno.get(g) and os.path.exists(f'{PREV}/p/{g}.p') and open(f'{PREV}/p/{g}.p').read() == txt:
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
    t0 = time.time()
    try:
        r = subprocess.run([TWEE, p] + base + hx + ['--quiet', '--no-proof'], capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        # (23 Nov) --backwards-goal 2 ran past the abstract-time limit (10 minutes, 5.8 GB): a row, not a crash
        return f'{g}\tTIMEOUT\t{time.time() - t0:.2f}\t-\t-\t0\n'
    dt = time.time() - t0
    ok = 'RESULT: Theorem' in r.stdout
    unp, pro, nk = '-', '-', 0
    if ok:
        r2 = subprocess.run([TWEE, p] + base + hx, capture_output=True, text=True, timeout=600)
        open(f'{OUT}/proofs/{g}', 'w').write(r2.stdout)
        used = [m[1] for l in r2.stdout.splitlines() for m in [AX.match(l)] if m]
        sib = [int(x[len('lemma_goal_'):]) for x in used if x.startswith('lemma_goal_')]
        nk = sum(1 for x in used if x.startswith('lemma_knn_'))
        u_ = [j for j in sib if f'{o}__goal_{j}' not in T]; p_ = [j for j in sib if f'{o}__goal_{j}' in T]
        unp = ','.join(map(str, sorted(u_))) or '-'; pro = ','.join(map(str, sorted(p_))) or '-'
    return f'{g}\t{"THM" if ok else "NO"}\t{dt:.2f}\t{unp}\t{pro}\t{nk}\n'
n = 0; th = 0
with open(RES, 'a') as fo, ThreadPoolExecutor(J) as ex:
    for line in ex.map(one, U):
        fo.write(line); fo.flush(); n += 1; th += line.split('\t')[1] == 'THM'
        if n % 200 == 0:
            print(f'condprove: {n}/{len(U)} THM {th} {time.strftime("%H:%M:%S")}', flush=True)
print(f'condprove: done {n} THM {th} {time.strftime("%H:%M:%S")}', flush=True)
