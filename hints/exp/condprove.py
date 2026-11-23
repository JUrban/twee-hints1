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
# (23 Nov, the step test bed) --after N: also the N nearest later siblings (any status; true as well); --args: more
# twee flags; --all: every goal of --only, solved or not
AFTER = int(opt('--after', '0')); XARGS = opt('--args', '').split(); ALL = '--all' in a
# --proved: siblings (earlier and --after later) only from TRUSTED, so every proof is a real one (no assumption)
PROVED = '--proved' in a
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
t_ = time.time()
index = lemmas.LemmaIndex(sorted(T), subsets=True) if KNN else None
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
    t0 = time.time()
    r = subprocess.run([TWEE, p] + base + ['--quiet', '--no-proof'], capture_output=True, text=True, timeout=600)
    dt = time.time() - t0
    ok = 'RESULT: Theorem' in r.stdout
    unp, pro, nk = '-', '-', 0
    if ok:
        r2 = subprocess.run([TWEE, p] + base, capture_output=True, text=True, timeout=600)
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
