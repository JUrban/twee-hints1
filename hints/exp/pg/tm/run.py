import subprocess, sys, time, resource, os, concurrent.futures as cf
S = sys.argv[1]
goals = open(S + '/tm/goals').read().split()
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); g = os.path.basename(w[1])[:-2]; cmds[g] = w
def variant(w, v, g):
    w = list(w)
    if v == 'dump': w += ['--dump-state', S + '/tm/%s.bin' % g]
    if v == 'nomodel':
        i = w.index('--rule-model'); del w[i:i+6]   # --rule-model M --rule-vocab V --rule-goal G
        j = w.index('--rule-threshold'); del w[j:j+4]
    if v == 'nohints':
        i = w.index('--hints-file'); del w[i:i+2]
    if v == 'startup':
        i = w.index('--max-time'); w[i+1] = '0.001'
    return w
def run(g, v):
    w = variant(cmds[g], v, g)
    t0 = time.time()
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    dt = time.time() - t0
    u, s_, m = p.stderr.decode().strip().split('\n')[-1].split()
    ok = b'HINTS-END' in p.stdout
    if v == 'dump' and os.path.exists(S + '/tm/%s.bin' % g):
        sz = os.path.getsize(S + '/tm/%s.bin' % g); os.unlink(S + '/tm/%s.bin' % g)
    else: sz = 0
    return g, v, dt, float(u) + float(s_), int(m), ok, sz
V = ['base', 'dump', 'nomodel', 'nohints', 'startup']
jobs = [(g, v) for g in goals for v in V]
with cf.ThreadPoolExecutor(3) as ex:
    res = list(ex.map(lambda x: run(*x), jobs))
import statistics, collections
by = collections.defaultdict(list)
for r in res: by[r[1]].append(r)
for v in V:
    R = by[v]
    print('%-8s wall med %.2f mean %.2f | cpu mean %.2f | maxrss med %d MB | proved %d | state MB mean %.1f' % (
        v, statistics.median(r[2] for r in R), statistics.mean(r[2] for r in R), statistics.mean(r[3] for r in R),
        statistics.median(r[4] for r in R) // 1024, sum(r[5] for r in R), statistics.mean(r[6] for r in R) / 1e6))
