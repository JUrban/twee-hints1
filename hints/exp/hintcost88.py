import json, subprocess, sys, os, resource, time
g, arm = sys.argv[1], sys.argv[2]
cap = '/project/hintwork/loops/P85C/cap'
r = next(json.loads(l) for l in open(f'{cap}/log.jsonl') if json.loads(l)['goal'] == g)
a = list(r['args']); drop = {'--print-given', '--print-given-unsolved', '--print-hints'}
out = []; i = 0
while i < len(a):
    if a[i] in drop: i += 1; continue
    if a[i] in ('--max-time', '--max-cpu'): i += 2; continue
    if arm == 'nohints' and a[i] == '--hints-file': i += 2; continue
    out.append(a[i]); i += 1
cmd = ['/project/bin/twee-e61'] + out + ['--max-time', '80', '--max-cpu', '1200'] + r['TWEE_PG_ARGS'].split()
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
o = p.stdout.read(); _, st, ru = os.wait4(p.pid, 0)
w = [l for l in o.splitlines() if l.startswith('WORK')]
res = 'THM' if 'RESULT: Theorem' in o or 'RESULT: Unsatisfiable' in o else 'NO'
print(f'{g}\t{arm}\t{res}\t{ru.ru_utime + ru.ru_stime:.1f}\t{w[0] if w else "-"}\t{ru.ru_maxrss // 1024} MB', flush=True)
