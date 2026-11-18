#!/usr/bin/env python3
"""exp5/run.py ARM T J [HEAP]: long runs on the exp3 goals that no arm proved at 320 abstract s.

Veroff's question (user, 17 Nov 19:xx): do much longer, hint-guided runs prove late goals, and does the rate of new
hint matches tell which runs to continue?
Goals: exp3/goals47 in order, each as soon as all four exp3 arms (C, K, E, V at 320) have it and none proved it.
The script polls exp3's result files every 60 s and ends when exp3 is complete and every eligible goal ran.
Command: exp3's (exp3/tb, production's context: twee-e48, PG 0.25, rm4t, sibling and kNN lemmas, the pool) for
arm ARM (C, K, E or V as in exp3), at T abstract s, CPU cap 10 T, --print-hint-matchers, +RTS -M<HEAP> (default 6g,
the binaries' own). No state dump: at 640 s it needs over 7 GB and memwatch.py kills it.
Workers: at most J; the file exp5/J sets the current limit, read before each run starts.
Writes res_<ARM>@T.tsv (goal, proved, CPU s, peak MB, considered pairs, matched hints, hints), out_<ARM>@T/<g>
(output without the given log), given_<ARM>@T/<g> for proofs."""
import concurrent.futures as cf, os, re, subprocess, sys, threading, time
E3 = '/project/hintwork/exp3'
arm, T, J = sys.argv[1], sys.argv[2], int(sys.argv[3])
HEAP = sys.argv[4] if len(sys.argv) > 4 else '6g'   # the binaries' own default, as in production
order = open(f'{E3}/goals47').read().split()
cmds = {}
for l in open(f'{E3}/tb/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
PROB = '/project/AIM60k/problems/tptp'
tag = f'{arm}@{T}'
for d in (f'out_{tag}', f'given_{tag}', f'states_{tag}'): os.makedirs(d, exist_ok=True)
def run(g):
    w = list(cmds[g])
    w[w.index('--max-time') + 1] = T; w[w.index('--max-cpu') + 1] = str(10 * float(T))
    hf = {'C': f'tb/tmp/{g}.hints', 'K': f'h_K/{g}.hints', 'E': f'h_E/{g}.hints', 'V': f'h_K/{g}.hints'}[arm]
    w[w.index('--hints-file') + 1] = f'{E3}/{hf}'
    if arm == 'V': w[1] = f'{PROB}/{g}.p'
    # no --dump-state: dumping a 640 s state takes over 7 GB, and memwatch.py (7 GB per twee) kills it (18 Nov 01:09)
    w += ['--print-hint-matchers', '+RTS', f'-M{HEAP}', '-RTS']
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_, mem = p.stderr.decode().strip().split('\n')[-1].split()
    out = p.stdout.decode('utf8', 'replace'); ok = 'HINTS-END' in out
    i, j = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
    open(f'out_{tag}/{g}', 'w').write(out[:i] + out[j:] if 0 <= i < j else out)
    if ok and 0 <= i < j: open(f'given_{tag}/{g}', 'w').write(out[i:j])
    m = re.search(r'WORK considered=(\d+)', out); h = re.search(r'HINTSTATS hints=(\d+) live=\d+ joined=\d+ matched=(\d+)', out)
    return g, float(u) + float(s_), int(mem) // 1024, ok, m.group(1) if m else '', h.group(2) if h else '', h.group(1) if h else ''
busy = [0]; lock = threading.Lock()
def limit():
    try: return max(1, min(J, int(open('J').read())))
    except (OSError, ValueError): return J
def gated(g):
    while True:
        with lock:
            if busy[0] < limit(): busy[0] += 1; break
        time.sleep(5)
    try: return run(g)
    finally:
        with lock: busy[0] -= 1
def exp3_state():
    res = {}
    for a in 'CKEV':
        p = f'{E3}/res_{a}@320.tsv'
        for l in open(p) if os.path.exists(p) else []:
            w = l.split('\t'); res.setdefault(w[0], {})[a] = w[1]
    eligible = [g for g in order if len(res.get(g, {})) == 4 and all(v == '0' for v in res[g].values())]
    complete = all(len(res.get(g, {})) == 4 for g in order)
    return eligible, complete
done = {l.split('\t')[0] for l in open(f'res_{tag}.tsv')} if os.path.exists(f'res_{tag}.tsv') else set()
f = open(f'res_{tag}.tsv', 'a'); submitted = set(done); futs = []
with cf.ThreadPoolExecutor(J) as ex:
    while True:
        eligible, complete = exp3_state()
        for g in eligible:
            if g not in submitted: submitted.add(g); futs.append(ex.submit(gated, g))
        for fu in [x for x in futs if x.done()]:
            g, cpu, mem, ok, cp, mt, nh = fu.result(); futs.remove(fu)
            f.write(f'{g}\t{int(ok)}\t{cpu:.1f}\t{mem}\t{cp}\t{mt}\t{nh}\n'); f.flush()
        if complete and not futs: break
        time.sleep(60)
