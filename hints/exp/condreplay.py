#!/usr/bin/env python3
"""condreplay.py OUT DIR... --trusted T.trusted [-j 2] [--time 60] [--tried FILE]: replay the climbers' conditional proofs whose
assumptions are now proved goals (24 Nov, exp75; notes/2026-11-24-cond-replay.md).

climb.py writes, for every sketch proof, DIR/used.tsv (target, tag, the axiom labels the proof used) and
DIR/assume.tsv (target, prefix, label, the goal an assumption states or '-', formula). A sketch proof of a still
unsolved target is ready when it proved the target itself (not a weakened goal: used.tsv column 5 is 0, or for older
rows the sketch's '# goal=' header is empty), each assume_* label it used stands for a goal in T, each lemma_goal_J
and lemma_knn_I_<goal> is in T, and an assumption from another original has the same or a subset of the target's
axioms. A label's goal is used.tsv column 4's (label=goal, climb.py since 24 Nov); for older rows assume.tsv's, and a
label written there more than once (kNN labels are rewritten as the list changes) is ready only when every goal it
stood for is in T. Labels '-' (theory conjectures) make a proof not ready. A proof that used a fill lemma (true_*) also gets all of the original's trusted
goals, as exp/fillcheck.py does, and the fill runs' hints (DIR/fillhints/<target>/*): the fill is re-derived, not
assumed.

The replay problem: the target's problem with these goals as lemma axioms (lemma_goal_J for the original's own goals,
lemma_knn_0_<goal> for another original's, the names condimport.py and trust.py resolve), the sketch's steps
(DIR/sketches/<target>/<tag>) as the hints file. twee-pg61 as condimport.py reruns it (no PG), --quiet --no-proof,
TIME abstract seconds. A target's ready proofs are tried in turn until one proves.

--tried FILE: proofs listed there (target, dir, tag) are skipped, and the ones tried are appended (abs/crploop.sh
reruns this hourly). Writes OUT/p/<goal>.p, OUT/h/<goal>.hints (the last tried problem), OUT/results.tsv (goal, THM/NO, seconds, climb dir,
tag, lemma axioms) and OUT/ready.tsv (every ready proof). Then: condimport.py OUT loops/<D> --trusted T --time TIME
and merge.py loops/UL loops/<D>."""
import collections, glob, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import lemmas

a = sys.argv[1:]


def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d


TR = opt('--trusted', ''); J = int(opt('-j', '2')); TM = opt('--time', '60'); TRIED = opt('--tried', '')
tried = {tuple(l.rstrip('\n').split('\t')[:3]) for l in open(TRIED)} if TRIED and os.path.exists(TRIED) else set()
OUT, DIRS = a[0], a[1:]
assert TR and DIRS, __doc__
T = {l.split()[0] for l in open(TR) if l.strip()}
S = {l.split('\t')[0] for l in open('/project/hintwork/loops/UL/solved.tsv') if l.strip()}
for d in ('p', 'h'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
AX = {}


def axioms(g):
    """the axiom lines of a goal's problem, without their names"""
    o = lemmas.split(g)[0]
    if o not in AX:
        AX[o] = {re.sub(r'^(fof|cnf)\([^,]*,', r'\1(', x.strip()) for x in open(os.path.join(lemmas.PROB, g + '.p'))
                 if x.startswith(('cnf(', 'fof(')) and 'conjecture' not in x}
    return AX[o]


ready = collections.defaultdict(list)   # target -> [(dir, tag, goals, fill)]
for D in DIRS:
    if not (os.path.exists(f'{D}/used.tsv') and os.path.exists(f'{D}/assume.tsv')):
        continue
    cand = collections.defaultdict(set)
    for l in open(f'{D}/assume.tsv'):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 5:
            cand[(w[0], w[2])].add(w[3])
    for l in open(f'{D}/used.tsv'):
        w = l.rstrip('\n').split('\t')
        if len(w) < 3 or w[0] in S:
            continue
        t, tag, labs = w[0], w[1], [x for x in w[2].split(',') if x]
        o = lemmas.split(t)[0]
        if not any(x.startswith('assume_') for x in labs):
            continue
        if len(w) >= 5:
            if w[4] != '0':
                continue
            exact = dict(x.split('=', 1) for x in w[3].split(',') if '=' in x)
        else:
            f_ = f'{D}/sketches/{t}/{tag}'
            if not os.path.exists(f_) or next((x[7:].strip() for x in open(f_) if x.startswith('# goal=')), ''):
                continue
            exact = None
        goals, ok, fill = set(), True, False
        for x in labs:
            if x.startswith('assume_'):
                c_ = {exact[x]} if exact is not None and x in exact else set(cand.get((t, x), ()))
                if not c_ or not all(s in T and (lemmas.split(s)[0] == o or axioms(s) <= axioms(t)) for s in c_):
                    ok = False; break
                goals |= c_
            elif x.startswith('lemma_goal_'):
                g = f'{o}__goal_{x[len("lemma_goal_"):]}'
                if g not in T:
                    ok = False; break
                goals.add(g)
            elif x.startswith('lemma_knn_'):
                m = re.fullmatch(r'lemma_knn_\d+_(.+__goal_\d+)', x)
                if not m or m[1] not in T:
                    ok = False; break
                goals.add(m[1])
            elif x.startswith('true_'):
                fill = True
        if ok and (t, D, tag) not in tried:
            ready[t].append((D, tag, goals, fill))
with open(os.path.join(OUT, 'ready.tsv'), 'w') as f:
    for t, rs in ready.items():
        for D, tag, goals, fill in rs:
            f.write(f'{t}\t{D}\t{tag}\t{int(fill)}\t{",".join(sorted(goals))}\n')
print(f'{sum(len(v) for v in ready.values())} ready conditional proofs of {len(ready)} unsolved targets', flush=True)


def problem(t, D, tag, goals, fill):
    o = lemmas.split(t)[0]
    src = [x for x in open(os.path.join(lemmas.PROB, t + '.p')) if x.startswith(('cnf(', 'fof('))]
    gs = set(goals)
    if fill:
        gs |= {g for g in T if lemmas.split(g)[0] == o}
    lines, n = [], 0
    for g in sorted(gs):
        lf = lemmas.lemma_form(g)
        if not lf:
            continue
        nm = f'lemma_goal_{g.rsplit("__goal_", 1)[1]}' if lemmas.split(g)[0] == o else f'lemma_knn_0_{g}'
        lines.append(f'fof({nm},axiom,{lf}).\n'); n += 1
    hs = [x for x in open(f'{D}/sketches/{t}/{tag}') if not x.startswith('#') and '\t' in x] \
        if os.path.exists(f'{D}/sketches/{t}/{tag}') else []
    if fill:
        for fh in sorted(glob.glob(f'{D}/fillhints/{t}/*')):
            hs += [x for x in open(fh) if not x.startswith('#') and '\t' in x]
    hs = list(dict.fromkeys(hs))
    return src[:-1] + lines + src[-1:] if 'conjecture' in src[-1] else src + lines, hs, n


env = dict(os.environ); env.pop('TWEE_PG_ARGS', None)


def run(t):
    for D, tag, goals, fill in ready[t]:
        pl, hs, n = problem(t, D, tag, goals, fill)
        p = os.path.join(OUT, 'p', t + '.p'); h = os.path.join(OUT, 'h', t + '.hints')
        open(p, 'w').writelines(pl); open(h, 'w').writelines(hs)
        t0 = time.time()
        try:
            r = subprocess.run(['/project/bin/twee-pg61', p, '--max-time', TM, '--abstract-time', '2000', '--no-colour',
                                '--no-resume-requeue', '--no-eqhint-consider', '--quiet', '--no-proof', '--hints-file', h],
                               capture_output=True, text=True, timeout=15 * float(TM) + 30, env=env).stdout
        except subprocess.TimeoutExpired:
            r = ''
        dt = time.time() - t0
        if 'RESULT: Theorem' in r:
            return t, 'THM', dt, D, tag, n
    return t, 'NO', dt, D, tag, n


with ThreadPoolExecutor(J) as ex, open(os.path.join(OUT, 'results.tsv'), 'a') as fo:
    k = 0
    for t, res, dt, D, tag, n in ex.map(run, sorted(ready)):
        fo.write(f'{t}\t{res}\t{dt:.2f}\t{os.path.basename(D)}\t{tag}\t{n}\n'); fo.flush(); k += res == 'THM'
        print(f'{res} {dt:6.1f}s {t} {os.path.basename(D)} {tag} lemmas {n}', flush=True)
if TRIED:
    with open(TRIED, 'a') as f:
        f.writelines(f'{t}\t{D}\t{tag}\n' for t, rs in ready.items() for D, tag, _, _ in rs)
print(f'{k} of {len(ready)} targets proved', flush=True)
