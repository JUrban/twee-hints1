#!/usr/bin/env python3
"""exp2/run.py VARIANTS J [GOALS]: the 200 frontier goals (pg/tb: captured in ORD's final context, lemmas,
rm4t, 5 abstract s) with twee-e48 and --pg-threshold 0.25 (production's settings since 17 Nov 19:00), the
hints file per variant: base = captured, xa = + expansion extras at the default factor, xw = extras at 0.1
(exp2/mkpools.py). Writes res_<v>.tsv: goal, proved, CPU s, considered pairs, matched hints; and the outputs
without their given logs in out_<v>/<g>."""
import concurrent.futures as cf, os, re, subprocess, sys
V = sys.argv[1].split(','); J = int(sys.argv[2])
goals = open(sys.argv[3] if len(sys.argv) > 3 else 'goals200').read().split()
cmds = {}
for l in open('/project/hintwork/pg/tb/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
HD = {'base': '/project/hintwork/pg/tb/tmp', 'xa': 'h_xa', 'xw': 'h_xw'}
def run(g, v):
    w = list(cmds[g]); w[0] = '/project/bin/twee-e48'
    w[w.index('--hints-file') + 1] = os.path.abspath(f'{HD[v]}/{g}.hints')
    w += ['--pg-threshold', '0.25']
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u, s_ = p.stderr.decode().strip().split('\n')[-1].split()
    out = p.stdout.decode('utf8', 'replace')
    i, j = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
    os.makedirs(f'out_{v}', exist_ok=True)
    open(f'out_{v}/{g}', 'w').write(out[:i] + out[j:] if 0 <= i < j else out)
    m = re.search(r'WORK considered=(\d+)', out); h = re.search(r'matched=(\d+)', out)
    return g, v, float(u) + float(s_), 'HINTS-END' in out, m.group(1) if m else '', h.group(1) if h else ''
fs = {v: open(f'res_{v}.tsv', 'a') for v in V}
with cf.ThreadPoolExecutor(J) as ex:
    for g, v, cpu, ok, cp, mt in ex.map(lambda x: run(*x), [(g, v) for g in goals for v in V]):
        fs[v].write(f'{g}\t{int(ok)}\t{cpu:.2f}\t{cp}\t{mt}\n'); fs[v].flush()
P = {v: {l.split('\t')[0] for l in open(f'res_{v}.tsv') if l.split('\t')[1] == '1'} for v in V}
for v in V:
    cpu = sum(float(l.split('\t')[2]) for l in open(f'res_{v}.tsv'))
    print(f'{v:5s} proved {len(P[v]):3d}  +{len(P[v] - P[V[0]])} -{len(P[V[0]] - P[v])} vs {V[0]}  CPU {cpu:.0f} s')
