#!/usr/bin/env python3
"""exp4/downhints.py SKETCH.tsv OUT.tsv [-j J] [--time T]: Veroff's down step with sketch hints.

For every goal with at least one proved sketch (sketch.py: an up move or a weaker goal), the real goal runs
without assumptions: the captured production command (exp3/tb: lemmas, the original's pool, rm4t, twee-e48,
PG 0.25) at T abstract s (default 80), the hints = the pool, then the steps of all its proved sketches (their
--print-hints lemmas and goal lines, canonical form, false ones included: hints only guide). The control needs no
run: abstract time is deterministic, so exp3's C@320 run of the same command proved within T abstract s iff its
critical pairs to proof are at most 2000 T.
--arms I,U: which sketches give hints, one run per goal and arm (interleaved by goal):
  I = the proofs of weaker goals (instances of the goal; true lemmas), U = the proofs in strengthened theories
  (steps may be false in T), A = both.
OUT.tsv: goal, arm, sketches used, sketch hints added, proved, CPU s, considered pairs, peak MB. Outputs in
OUT.d/<arm>/."""
import argparse, collections, concurrent.futures as cf, os, re, subprocess, sys
sys.path.insert(0, '/project/twee/hints')
import hintlib
TB = '/project/hintwork/exp3/tb'
cmds = {}
for l in open(f'{TB}/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
ap = argparse.ArgumentParser(); ap.add_argument('sketch'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=2); ap.add_argument('--time', type=float, default=80)
ap.add_argument('--arms', default='I,U')
ap.add_argument('--factor', type=float, help="the sketch hints' own score factor (hints file column 3; default: twee's --eqhint-factor, 0.01; lower is stronger)")
a = ap.parse_args()
sk = collections.defaultdict(list)
for l in open(a.sketch):
    w = l.rstrip('\n').split('\t')
    if len(w) >= 5 and w[4] == '1': sk[w[0]].append((w[1], 'I' if w[2] == 'inst' else 'U'))
sd = a.sketch + '.d'
def run(job):
    g, arm = job; mids = [m for m, k in sk[g] if arm == 'A' or k == arm]
    sig = hintlib.problem_signature(g)
    pool = open(f'{TB}/tmp/{g}.hints').read().splitlines()
    seen = {tuple(x.split('\t')[:2]) for x in pool}; extra = []
    for mid in mids:
        L, G = hintlib.extract_hints(open(f'{sd}/{g}.{mid}.out', errors='replace').read())
        for l, r in L + G:
            if l == r: continue
            k = min(hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig))
            if k[0] != k[1] and k not in seen: seen.add(k); extra.append(k)
    od = f'{a.out}.d/{arm}'; os.makedirs(od, exist_ok=True); hf = f'{od}/{g}.hints'
    fac = [] if a.factor is None else [str(a.factor)]
    open(hf, 'w').write('\n'.join(pool + ['\t'.join(list(k) + fac) for k in extra]) + '\n')
    w = list(cmds[g]); T = a.time
    w[w.index('--max-time') + 1] = str(T); w[w.index('--max-cpu') + 1] = str(10 * T)
    w[w.index('--hints-file') + 1] = os.path.abspath(hf)
    w = [x for x in w if x != '--print-given']
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_, mem = p.stderr.decode().strip().split('\n')[-1].split()
    out = p.stdout.decode('utf8', 'replace'); open(f'{od}/{g}', 'w').write(out)
    m = re.search(r'WORK considered=(\d+)', out)
    return [g, arm, len(mids), len(extra), int('HINTS-END' in out), f'{float(u) + float(s_):.1f}', m.group(1) if m else '', int(mem) // 1024]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    jobs = [(g, arm) for g in sorted(sk) for arm in a.arms.split(',') if any(arm == 'A' or k == arm for _, k in sk[g])]
    for res in ex.map(run, jobs):
        f.write('\t'.join(map(str, res)) + '\n'); f.flush()
