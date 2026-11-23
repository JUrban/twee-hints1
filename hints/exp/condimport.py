"""condimport.py SRC DEST [--time 5] [--trusted T.trusted] [--only GOALS]: exp/condprove.py --proved proofs of SRC
(a cond/ dir) as a loop dir DEST (under loops/) that merge.py can take into production, with the record trust.py
needs.

For each THM row of SRC/results.tsv whose problem SRC/p/<goal>.p has only lemma axioms naming trusted goals
(lemma_goal_J: the goal's original's goal J; lemma_knn_I_<goal>), the problem is rerun the way loop.py runs it
(--quiet --no-proof --print-hints --print-given, the same flags as condprove.py). If twee proves it again and every
name in its USEDAXIOMS line resolves to a trusted goal:
  DEST/r1/out/<goal>   the kept output (RESULT, HINTS, USEDAXIOMS),
  DEST/hints/<goal>    the proof's hints, canonical as loop.py writes them (loop.canon_key),
  DEST/solved.tsv      <goal> 1 <seconds>,
  DEST/proofs/<goal>   the printed proof (a third run with the proof on),
  DEST/p/<goal>.p      the problem.
Goals that fail any check are listed with the reason. Then: python3 merge.py loops/UL DEST --dry, and without --dry."""
import os, re, sys, subprocess, time
sys.path.insert(0, '/project/twee/hints')
import hintlib, loop
a = sys.argv[1:]
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
TM = opt('--time', '5'); TR = opt('--trusted', '/project/hintwork/loops/TRUSTNOW/t2139.trusted'); ONLY = opt('--only', '')
SRC, DEST = a
TWEE = '/project/bin/twee-pg61'
T = {l.split()[0] for l in open(TR) if l.strip()}
base = ['--max-time', TM, '--abstract-time', '2000', '--no-colour', '--no-resume-requeue', '--no-eqhint-consider']
rows = [l.rstrip('\n').split('\t') for l in open(f'{SRC}/results.tsv') if l.strip()]
goals = [r[0] for r in rows if r[1] == 'THM']
if ONLY:
    keep = {l.strip() for l in open(ONLY) if l.strip()}; goals = [g for g in goals if g in keep]
for d in ('r1/out', 'hints', 'proofs', 'p'):
    os.makedirs(f'{DEST}/{d}', exist_ok=True)
have = {l.split('\t')[0] for l in open(f'{DEST}/solved.tsv')} if os.path.exists(f'{DEST}/solved.tsv') else set()
def resolve(name, o):
    """the trusted goal a lemma axiom name stands for, or None"""
    m = re.fullmatch(r'lemma_goal_(\d+)', name)
    if m:
        g = f'{o}__goal_{m[1]}'
        return g if g in T else None
    m = re.fullmatch(r'lemma_knn_\d+_(.+__goal_\d+)', name)
    if m:
        return m[1] if m[1] in T else None
    return None
env = dict(os.environ); env.pop('TWEE_PG_ARGS', None)   # (as condprove.py ran: no PG, no branch limit)
ok_n = 0
with open(f'{DEST}/solved.tsv', 'a') as sf:
    for g in goals:
        if g in have or g in T:
            continue
        o = g.rsplit('__goal_', 1)[0]
        src = open(f'{SRC}/p/{g}.p').read()
        names = re.findall(r'fof\((lemma_\w+),axiom,', src)
        bad = [n for n in names if resolve(n, o) is None]
        if bad:
            print(f'{g}\tskip: lemma axioms not trusted: {" ".join(bad[:5])}'); continue
        p = f'{DEST}/p/{g}.p'
        open(p, 'w').write(src)
        t0 = time.time()
        r = subprocess.run([TWEE, p] + base + ['--quiet', '--no-proof', '--print-hints', '--print-given'],
                           capture_output=True, text=True, timeout=600, env=env)
        dt = time.time() - t0; out = r.stdout
        if 'RESULT: Theorem' not in out:
            print(f'{g}\tskip: not proved again ({dt:.1f}s)'); continue
        used = next((l.split()[1:] for l in out.splitlines() if l.startswith('USEDAXIOMS')), None)
        if used is None:
            print(f'{g}\tskip: no USEDAXIOMS'); continue
        ubad = [n for n in used if n.startswith('lemma_') and resolve(n, o) is None]
        if ubad:
            print(f'{g}\tskip: used {" ".join(ubad)}'); continue
        L, Gl = hintlib.extract_hints(out)
        sig = hintlib.problem_signature(g)
        seen, hs = set(), []
        for l, rr in L + Gl:
            if l == rr:
                continue
            k = loop.canon_key(l, rr, sig)
            if k[0] == k[1] or k in seen:
                continue
            seen.add(k); hs.append(k)
        open(f'{DEST}/r1/out/{g}', 'w').write(out)
        with open(f'{DEST}/hints/{g}', 'w') as hf:
            for l, rr in hs:
                hf.write(f'{l}\t{rr}\n')
        r2 = subprocess.run([TWEE, p] + base, capture_output=True, text=True, timeout=600, env=env)
        open(f'{DEST}/proofs/{g}', 'w').write(r2.stdout)
        sf.write(f'{g}\t1\t{dt:.2f}\n'); sf.flush(); ok_n += 1
        print(f'{g}\tok {dt:.2f}s, {len(hs)} hints, used {" ".join(sorted(n for n in used if n.startswith("lemma_")))}')
print(f'condimport: {ok_n} of {len(goals)} into {DEST}')
