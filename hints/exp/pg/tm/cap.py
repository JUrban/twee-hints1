import subprocess, sys, os, concurrent.futures as cf
S = sys.argv[1]; goals = open(S + '/tm/all.goals').read().split(); V = sys.argv[2].split(',')
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def run(g, v):
    w = list(cmds[g]); w[0] = '/project/bin/twee-e44'
    if v != 'none': w += ['--max-term-size', v]
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_ = p.stderr.decode().strip().split('\n')[-1].split()
    return g, v, float(u) + float(s_), b'HINTS-END' in p.stdout
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(lambda x: run(*x), [(g, v) for g in goals for v in V]))
P = {v: set(r[0] for r in res if r[1] == v and r[3]) for v in V}
for v in V:
    R = [r for r in res if r[1] == v]
    print('cap %-5s cpu %.0f s  proved %d  (+%d -%d vs none)' % (v, sum(r[2] for r in R), len(P[v]), len(P[v] - P['none']), len(P['none'] - P[v])))
