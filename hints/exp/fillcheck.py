#!/usr/bin/env python3
"""fillcheck.py TRUSTRUN [-j 2] [--time 60]: re-prove, with their premises recorded, the old fill lemmas that
production's untrusted proofs use (23 Nov, notes/2026-11-23-climber-restart.md "Fill lemmas get a premise record").

A fill lemma (climb.py --fill) proved before 23 Nov 23:03 has no premise record, so trust.py cannot trust a
production proof in an exposed original that uses it (loop.py --climb-hints gives them as lemma_fill_N). TRUSTRUN is
a trust.py output prefix (loops/TRUSTNOW/tHHMM). For each goal of TRUSTRUN.roots whose printed proof
(loops/UL/proofs/<goal>) has lemma_fill_N axioms, each such formula becomes the conjecture of a problem with the
original's axioms and all its trusted goals (TRUSTRUN.trusted) as lemma axioms (lemma_goal_J, unitized as in
lemmas.lemma_problem), production's hints of the goal as hints; twee-pg61 --print-hints, TIME abstract seconds.
Appends to loops/TRUSTNOW/fillcheck.tsv: original, formula (as the proof prints it), proved 0/1, premises (the
lemma names of USEDAXIOMS), seconds, the goal. trust.py reads the proved rows as fill lemmas with a record."""
import os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import lemmas

L = '/project/hintwork/loops'
a = sys.argv[1:]
J = int(a[a.index('-j') + 1]) if '-j' in a else 2
TM = float(a[a.index('--time') + 1]) if '--time' in a else 60
R = a[0]
OUT = os.path.join(L, 'TRUSTNOW', 'fillcheck.tsv')
TMP = os.path.join(L, 'TRUSTNOW', 'fillcheck.tmp')
os.makedirs(TMP, exist_ok=True)
tr = {l.strip() for l in open(R + '.trusted') if l.strip()}
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 3:
            done.add((w[0], w[1]))
todo = []
for g in (l.strip() for l in open(R + '.roots') if l.strip()):
    pf = os.path.join(L, 'UL', 'proofs', g)
    if not os.path.exists(pf):
        continue
    for m in re.finditer(r'^Axiom \d+ \((lemma_fill_\d+)\): (.*)\.$', open(pf, errors='replace').read(), re.M):
        k = (lemmas.split(g)[0], m.group(2))
        if k not in done and k not in {x[:2] for x in todo}:
            todo.append((k[0], k[1], g))
print(f'{len(todo)} fill lemmas to check ({len(done)} checked before)', flush=True)


def check(i_x):
    i, (o, f, g) = i_x
    lines = [x for x in open(os.path.join(lemmas.PROB, g + '.p')) if x.startswith(('cnf(', 'fof(')) and 'conjecture' not in x]
    sib = sorted(int(x.rsplit('__goal_', 1)[1]) for x in tr if lemmas.split(x)[0] == o)
    for j in sib:
        lf = lemmas.lemma_form(f'{o}__goal_{j}')
        if lf:
            lines.append(f'fof(lemma_goal_{j},axiom,{lf}).\n')
    vs = sorted(set(re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', f)))
    l_, r_ = f.split(' = ', 1)
    lines.append(f'fof(fill_check,conjecture,{"! [" + ",".join(vs) + "] : " if vs else ""}({l_} = {r_})).\n')
    p = os.path.join(TMP, f'{g}.{i}.p')
    open(p, 'w').writelines(lines)
    cmd = ['/project/bin/twee-pg61', p, '--max-time', str(TM), '--no-colour', '--quiet', '--no-proof', '--print-hints',
           '--abstract-time', '2000', '--no-eqhint-consider', '--max-cpu', str(10 * TM)]
    hf = os.path.join(L, 'UL', 'hints', g)
    if os.path.exists(hf):
        cmd += ['--hints-file', hf]
    env = dict(os.environ, TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100')
    t0 = time.time()
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                             timeout=15 * TM + 30).stdout.decode('utf8', 'replace')
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b'').decode('utf8', 'replace')
    dt = time.time() - t0
    ok = 'RESULT: Theorem' in out
    ua = next((x.split()[1:] for x in out.splitlines() if x.startswith('USEDAXIOMS')), [])
    os.unlink(p)
    return o, f, int(ok), ','.join(sorted(x for x in ua if x.startswith('lemma_'))), dt, g


with ThreadPoolExecutor(J) as ex, open(OUT, 'a') as fo:
    n = 0
    for o, f, ok, prem, dt, g in ex.map(check, enumerate(todo)):
        fo.write(f'{o}\t{f}\t{ok}\t{prem}\t{dt:.1f}\t{g}\n'); fo.flush(); n += ok
        print(f'{ok} {dt:6.1f}s {o} {f[:90]}', flush=True)
print(f'{n} of {len(todo)} proved', flush=True)
