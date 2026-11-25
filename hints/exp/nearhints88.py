"""(25 Nov, exp88b) a capture of exp85 (loops/P85C/cap) with its hints file replaced by the proof steps of the K solved
siblings nearest by goal number (solved before the capture: loops/UL/hints/<sib> older than the capture's hints file).
Usage: nearhints88.py GOAL K OUTDIR -> one row: goal, arm, result, CPU s, WORK line, max RSS"""
import json, subprocess, sys, os, re
g, K, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
cap = '/project/hintwork/loops/P85C/cap'; H = '/project/hintwork/loops/UL/hints'
r = next(json.loads(l) for l in open(f'{cap}/log.jsonl') if json.loads(l)['goal'] == g)
a = list(r['args'])
hf = a[a.index('--hints-file') + 1]
t0 = os.path.getmtime(hf if os.path.isabs(hf) else os.path.join(r['cwd'], hf))
o, n = g.rsplit('__goal_', 1); n = int(n)
sib = []
for f in os.listdir(H):
    if f.startswith(o + '__goal_') and f != g:
        m = int(f.rsplit('_', 1)[1])
        if os.path.getmtime(os.path.join(H, f)) < t0:
            sib.append((abs(m - n), m, f))
sib.sort()
seen, hints = set(), []
for _, _, f in sib[:K]:
    for l in open(os.path.join(H, f)):
        h = tuple(l.rstrip('\n').split('\t')[:2])
        if len(h) == 2 and h not in seen:
            seen.add(h); hints.append(h)
os.makedirs(out, exist_ok=True)
hp = os.path.join(out, f'{g}.near{K}.hints')
with open(hp, 'w') as f:
    f.writelines('\t'.join(h) + '\n' for h in hints)
drop = {'--print-given', '--print-given-unsolved', '--print-hints'}
cmd = []; i = 0
while i < len(a):
    if a[i] in drop: i += 1; continue
    if a[i] in ('--max-time', '--max-cpu'): i += 2; continue
    if a[i] == '--hints-file': cmd += ['--hints-file', hp]; i += 2; continue
    cmd.append(a[i]); i += 1
cmd = ['/project/bin/twee-e61'] + cmd + ['--max-time', '80', '--max-cpu', '1200'] + r['TWEE_PG_ARGS'].split()
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=r['cwd'])
so = p.stdout.read(); _, st, ru = os.wait4(p.pid, 0)
w = [l for l in so.splitlines() if l.startswith('WORK')]
res = 'THM' if 'RESULT: Theorem' in so or 'RESULT: Unsatisfiable' in so else 'NO'
print(f'{g}\tnear{K}\t{res}\t{ru.ru_utime + ru.ru_stime:.1f}\t{w[0] if w else "-"}\t{ru.ru_maxrss // 1024} MB\t{len(sib[:K])} sibs {len(hints)} hints', flush=True)
