#!/usr/bin/env python3
"""exp3/run.py ARMS T J [GOALS] (J at most; the file exp3/J sets the current limit): deep runs on 48 late unsolved goals (exp3/goals48), T abstract s, CPU cap 10 T.
Commands captured in production's context (loops/UL, solve_new.sh defaults: twee-e48, PG 0.25, rm4t, sibling
and kNN lemmas, the original's pool), in exp3/tb. Arms: C = as captured; K = the lemmas, hints = the expanded
chain of the 10 nearest proven siblings below (h_K); E = pool + chain extras (h_E); V = the original problem
from the axioms alone, hints = the chain. Writes res_<arm>@T.tsv: goal, proved, CPU s, peak MB, considered
pairs, matched hints, hints; out_<arm>@T/<g> (without the given log, with HINTLOG for stallsim.py), and for
proved runs given_<arm>@T/<g> (the given log, training data of long proofs)."""
import concurrent.futures as cf, os, re, subprocess, sys
A = sys.argv[1].split(','); T = sys.argv[2]; J = int(sys.argv[3])
goals = open(sys.argv[4] if len(sys.argv) > 4 else 'goals47').read().split()
cmds = {}
for l in open('tb/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
PROB = '/project/AIM60k/problems/tptp'
def run(g, a):
    w = list(cmds[g])
    w[w.index('--max-time') + 1] = T; w[w.index('--max-cpu') + 1] = str(10 * float(T))
    hf = {'C': f'tb/tmp/{g}.hints', 'K': f'h_K/{g}.hints', 'E': f'h_E/{g}.hints', 'V': f'h_K/{g}.hints'}[a]
    w[w.index('--hints-file') + 1] = os.path.abspath(hf)
    if a == 'V': w[1] = f'{PROB}/{g}.p'
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_, mem = p.stderr.decode().strip().split('\n')[-1].split()
    out = p.stdout.decode('utf8', 'replace'); ok = 'HINTS-END' in out
    tag = f'{a}@{T}'
    i, j = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
    for d in (f'out_{tag}', f'given_{tag}'): os.makedirs(d, exist_ok=True)
    open(f'out_{tag}/{g}', 'w').write(out[:i] + out[j:] if 0 <= i < j else out)
    if ok and 0 <= i < j: open(f'given_{tag}/{g}', 'w').write(out[i:j])
    m = re.search(r'WORK considered=(\d+)', out); h = re.search(r'HINTSTATS hints=(\d+) live=\d+ joined=\d+ matched=(\d+)', out)
    return g, tag, float(u) + float(s_), int(mem) // 1024, ok, m.group(1) if m else '', h.group(2) if h else '', h.group(1) if h else ''
# J is the most workers; the file exp3/J (if present) sets the current limit, read before each run starts
import threading, time
busy = [0]; lock = threading.Lock()
def limit():
    try: return max(1, min(J, int(open('J').read())))
    except (OSError, ValueError): return J
def gated(x):
    while True:
        with lock:
            if busy[0] < limit(): busy[0] += 1; break
        time.sleep(5)
    try: return run(*x)
    finally:
        with lock: busy[0] -= 1
fs = {a: open(f'res_{a}@{T}.tsv', 'a') for a in A}
with cf.ThreadPoolExecutor(J) as ex:
    futs = [ex.submit(gated, (g, a)) for g in goals for a in A]
    for fu in cf.as_completed(futs):
        g, tag, cpu, mem, ok, cp, mt, nh = fu.result()
        fs[tag.split('@')[0]].write(f'{g}\t{int(ok)}\t{cpu:.1f}\t{mem}\t{cp}\t{mt}\t{nh}\n'); fs[tag.split('@')[0]].flush()
P = {a: {l.split('\t')[0] for l in open(f'res_{a}@{T}.tsv') if l.split('\t')[1] == '1'} for a in A}
for a in A:
    cpu = sum(float(l.split('\t')[2]) for l in open(f'res_{a}@{T}.tsv'))
    print(f'{a}@{T} proved {len(P[a]):3d}  +{len(P[a] - P[A[0]])} -{len(P[A[0]] - P[a])} vs {A[0]}  CPU {cpu:.0f} s')
