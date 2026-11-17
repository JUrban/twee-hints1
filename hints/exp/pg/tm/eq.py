import subprocess, sys, os, time, hashlib, concurrent.futures as cf, re
S = sys.argv[1]; bins = sys.argv[2].split(','); goals = open(S + '/tm/' + sys.argv[3]).read().split()
cmds = {}
for l in open(S + '/tm/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
def run(g, b):
    w = list(cmds[g]); w[0] = b
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_ = p.stderr.decode().strip().split('\n')[-1].split()
    out = p.stdout
    hs = re.search(rb'HINTSTATS[^\n]*', out)
    return g, b, float(u) + float(s_), hashlib.md5(out).hexdigest(), b'HINTS-END' in out, hs.group(0).decode() if hs else ''
jobs = [(g, b) for g in goals for b in bins]
with cf.ThreadPoolExecutor(int(sys.argv[4])) as ex:
    res = list(ex.map(lambda x: run(*x), jobs))
R = {(r[0], r[1]): r for r in res}
same = diff = 0; cpu = {b: 0.0 for b in bins}; prov = {b: 0 for b in bins}
for g in goals:
    a, b = R[(g, bins[0])], R[(g, bins[1])]
    for x in (a, b): cpu[x[1]] += x[2]; prov[x[1]] += x[4]
    if a[3] == b[3]: same += 1
    else:
        diff += 1; print('DIFF', g, a[4], b[4], '|', a[5][:120], '|', b[5][:120])
print('identical output', same, 'differ', diff)
for b in bins: print(b, 'cpu %.1f' % cpu[b], 'proved', prov[b])
