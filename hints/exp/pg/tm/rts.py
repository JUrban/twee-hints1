import subprocess, sys, os, concurrent.futures as cf, statistics, hashlib
S = sys.argv[1]; goals = open(S + '/tm/goals').read().split(); V = sys.argv[2].split(',')
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def run(g, v):
    w = list(cmds[g]); w[0] = '/project/bin/twee-e44'
    if v != 'default': w += ['+RTS'] + v.split() + ['-RTS']
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_, m = p.stderr.decode().strip().split('\n')[-1].split()
    return g, v, float(u) + float(s_), int(m), hashlib.md5(p.stdout).hexdigest()
with cf.ThreadPoolExecutor(3) as ex:
    res = list(ex.map(lambda x: run(*x), [(g, v) for g in goals for v in V]))
base = {r[0]: r[4] for r in res if r[1] == V[0]}
for v in V:
    R = [r for r in res if r[1] == v]
    print('%-12s cpu mean %.2f  maxrss med %d MB  same output as %s: %d/%d' % (v, statistics.mean(r[2] for r in R),
          statistics.median(r[3] for r in R) // 1024, V[0], sum(base[r[0]] == r[4] for r in R), len(R)))
