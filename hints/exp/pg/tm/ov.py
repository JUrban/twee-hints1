import subprocess, sys, os, concurrent.futures as cf, statistics
S = sys.argv[1]; goals = open(S + '/tm/goals').read().split()
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def run(g, v):
    w = list(cmds[g]); env = dict(os.environ)
    if v != 'e44': w[0] = '/project/bin/twee-e44x'
    if v in ('f1', 'f1nolook'): w += ['--eqhint-factor', '1']
    if v == 'f1nolook': env['TWEE_HINT_NOLOOKUP'] = '1'
    if v == 'nohints': i = w.index('--hints-file'); del w[i:i+2]
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    u, s_ = p.stderr.decode().strip().split('\n')[-1].split()
    return v, float(u) + float(s_)
V = ['e44', 'f1', 'f1nolook', 'nohints']
with cf.ThreadPoolExecutor(3) as ex:
    res = list(ex.map(lambda x: run(*x), [(g, v) for g in goals for v in V]))
for v in V: print(v, 'cpu mean %.2f' % statistics.mean(c for vv, c in res if vv == v))
