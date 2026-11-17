#!/usr/bin/env python3
"""exp4/refine.py SKETCH.tsv OUT.tsv [-j J] [--time T]: the refinement (down) step of stage 1.

For every sketch that proved its goal using its assumption S (sketch.py), the used instances of S that Mace4 did
not refute in the real theory T become separate assumptions (fof(assume_<i>, axiom, ...)); the refuted ones are
left out. The goal's captured production command (exp3/tb) runs again at T abstract s (default 5) with them.
Per goal one more run ('all') gives the plausible instances of all its proved sketches together.
If the run proves the goal, the assumptions it used (USEDAXIOMS) are the rung: conjectures plausible in T
(no countermodel up to 8) that suffice for the goal; if it used none, it is a real proof.
OUT.tsv: goal, source (move id or 'all'), assumptions given, proved, used, CPU s, the used conjectures (; sep.).
Outputs in OUT.d/<goal>.<source>."""
import argparse, collections, concurrent.futures as cf, os, re, subprocess
TB = '/project/hintwork/exp3/tb'
cmds = {}
for l in open(f'{TB}/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def run(g, src, conj, T, out_dir):
    w = list(cmds[g]); prob = open(w[1]).read()
    for i, c in enumerate(conj):
        vs = sorted(set(re.findall(r'\bX\d+\b', c)), key=lambda v: int(v[1:]))
        prob += f"\nfof(assume_{i},axiom,{'! [' + ','.join(vs) + '] : ' if vs else ''}{c}).\n"
    os.makedirs(out_dir, exist_ok=True); pp = f'{out_dir}/{g}.{src}.p'; open(pp, 'w').write(prob)
    w[1] = pp; w[w.index('--max-time') + 1] = str(T); w[w.index('--max-cpu') + 1] = str(10 * T)
    w = [x for x in w if x not in ('--no-proof', '--print-given')]
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cpu = sum(float(x) for x in p.stderr.decode().strip().split('\n')[-1].split())
    out = p.stdout.decode('utf8', 'replace'); open(f'{out_dir}/{g}.{src}.out', 'w').write(out)
    ok = 'RESULT: Theorem' in out
    m = re.search(r'^USEDAXIOMS(.*)$', out, re.M)
    used = sorted(int(x[7:]) for x in (m.group(1).split() if m else []) if re.match(r'assume_\d+$', x))
    return [g, src, len(conj), int(ok), len(used) if ok else '', f'{cpu:.1f}', '; '.join(conj[i] for i in used) if ok else '']
ap = argparse.ArgumentParser(); ap.add_argument('sketch'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=2); ap.add_argument('--time', type=float, default=5)
a = ap.parse_args()
jobs, per_goal = [], collections.defaultdict(list)
for l in open(a.sketch):
    w = l.rstrip('\n').split('\t')
    if len(w) < 11 or w[4] != '1' or w[5] != '1': continue
    conj = [c for c in w[10].split('; ') if c and not c.startswith('x ')]
    if not conj: continue
    jobs.append((w[0], w[1], conj))
    for c in conj:
        if c not in per_goal[w[0]]: per_goal[w[0]].append(c)
jobs += [(g, 'all', cs) for g, cs in per_goal.items()]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for res in ex.map(lambda x: run(*x, a.time, a.out + '.d'), jobs):
        f.write('\t'.join(map(str, res)) + '\n'); f.flush()
