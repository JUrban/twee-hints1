import subprocess, sys, os, concurrent.futures as cf
S = sys.argv[1]; goals = open(S + '/tm/all.goals').read().split(); V = sys.argv[2].split(';')
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def variant(w, v):
    w = list(w); w[0] = '/project/bin/twee-e48'
    if v == 'base': return w
    if v == 'nomodel':
        i = w.index('--rule-model'); del w[i:i+6]; j = w.index('--rule-threshold'); del w[j:j+4]; return w
    for kv in v.split(','):
        k, x = kv.split('=')
        if k in w: w[w.index(k) + 1] = x
        else: w += [k, x]
    return w
def run(g, v):
    w = variant(cmds[g], v)
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_ = p.stderr.decode().strip().split('\n')[-1].split()
    return g, v, float(u) + float(s_), b'HINTS-END' in p.stdout
with cf.ThreadPoolExecutor(int(sys.argv[3])) as ex:
    res = list(ex.map(lambda x: run(*x), [(g, v) for g in goals for v in V]))
P = {v: set(r[0] for r in res if r[1] == v and r[3]) for v in V}
for v in V:
    R = [r for r in res if r[1] == v]
    print('%-50s cpu %4.0f s  proved %2d  (+%d -%d vs %s)' % (v, sum(r[2] for r in R), len(P[v]), len(P[v] - P[V[0]]), len(P[V[0]] - P[v]), V[0]))
