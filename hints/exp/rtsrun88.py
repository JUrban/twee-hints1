import json, subprocess, sys, os, resource, time
g, tag, rts = sys.argv[1], sys.argv[2], sys.argv[3:]
cap = '/project/hintwork/loops/P85C/cap'
r = next(json.loads(l) for l in open(f'{cap}/log.jsonl') if json.loads(l)['goal'] == g)
a = list(r['args']); drop = {'--print-given', '--print-given-unsolved', '--print-hints'}
out = []; i = 0
while i < len(a):
    if a[i] in drop: i += 1; continue
    if a[i] in ('--max-time', '--max-cpu'): i += 2; continue
    out.append(a[i]); i += 1
cmd = [os.environ.get('TW', '/project/bin/twee-e61')] + out + ['--max-time', os.environ.get('MT', '160'), '--max-cpu', '3600'] + r['TWEE_PG_ARGS'].split() + ['+RTS', '-s'] + rts + ['-RTS']
t0 = time.time()
p = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
open(f'{tag}.out', 'w').write(p.stdout[-3000:] + '\n---\n' + p.stderr[-4000:])
print(tag, 'wall %.0f' % (time.time() - t0), [l for l in p.stdout.splitlines() if l.startswith('WORK') or l.startswith('RESULT')])
