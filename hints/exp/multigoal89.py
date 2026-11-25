"""(25 Nov, exp89; the user: Prover9 keeps going after the first goal and reports each proved one; would that spare
repeating long runs?) A capture of exp85 (loops/P85C/cap) run as is plus the negated, Skolemised conjectures of up to K
siblings of its original that are unsolved now (nearest by goal number, within D), with --multi-goal, to T abstract s.
Prints the target's result and each extra goal's SOLVEDGOAL (name, considered pairs).
Usage: multigoal89.py GOAL K D T OUTDIR"""
import json, subprocess, sys, os, re
g, K, D, T, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
cap = '/project/hintwork/loops/P85C/cap'; PROB = '/project/AIM60k/problems/tptp'
S = {l.split('\t')[0] for l in open('/project/hintwork/loops/UL/solved.tsv')}
allg = [l.split()[0] for l in open('/project/hintwork/sets/all')]
r = [json.loads(l) for l in open(f'{cap}/log.jsonl') if json.loads(l)['goal'] == g][-1]
o, n = g.rsplit('__goal_', 1); n = int(n)
sib = sorted((abs(int(m.rsplit('__goal_', 1)[1]) - n), m) for m in allg
             if m.startswith(o + '__goal_') and m != g and m not in S)
extra = [m for d, m in sib if d <= D][:K]
a = list(r['args'])
src = next(x for x in a if x.endswith('.p'))
lines = open(src).read()
add = []
for i, m in enumerate(extra):
    c = next(l for l in open(f'{PROB}/{m}.p') if l.startswith('fof(') and ',conjecture,' in l.replace(' ', ''))
    body = c.split(',conjecture,', 1)[1].rsplit(').', 1)[0].strip()
    vs = []
    while True:
        mm = re.match(r'!\s*\[([^\]]*)\]\s*:\s*(.*)', body, re.S)
        if not mm: break
        vs += [v.strip() for v in mm.group(1).split(',')]; body = mm.group(2).strip()
    l_, r_ = body.split(' = ', 1)
    sub = {v: f'skmg{i}_{v.lower()}' for v in vs}
    f = lambda x: re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', lambda q: sub[q.group(0)], x)
    add.append(f'cnf(mg_{m}, negated_conjecture, {f(l_)} != {f(r_)}).\n')   # (a clause name may not start upper-case)
os.makedirs(out, exist_ok=True)
pp = os.path.join(out, g + '.mg.p')
with open(pp, 'w') as fh:
    fh.write(lines + ('' if lines.endswith('\n') else '\n') + ''.join(add))
drop = {'--print-given', '--print-given-unsolved', '--print-hints'}
cmd = []; i = 0
while i < len(a):
    if a[i] in drop: i += 1; continue
    if a[i] in ('--max-time', '--max-cpu'): i += 2; continue
    if a[i] == src: cmd.append(pp); i += 1; continue
    cmd.append(a[i]); i += 1
cmd = ['/project/bin/twee-e61'] + cmd + ['--max-time', T, '--max-cpu', str(int(float(T) * 10)), '--multi-goal'] + r['TWEE_PG_ARGS'].split()
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=r['cwd'])
so = p.stdout.read(); _, st, ru = os.wait4(p.pid, 0)
open(os.path.join(out, g + '.mg.out'), 'w').write(''.join(l + '\n' for l in so.splitlines() if l.startswith(('SOLVEDGOAL', 'WORK', 'RESULT'))))
sg = [(re.sub(r'^mg_', '', l.split()[1]), l.split()[2].split('=')[1]) for l in so.splitlines() if l.startswith('SOLVEDGOAL ')]
w = [l for l in so.splitlines() if l.startswith('WORK')]
tg = [c for nm, c in sg if nm not in extra]
ex = [f'{nm}@{c}' for nm, c in sg if nm in extra]
print(f'{g}\t{len(extra)}\t{"THM@" + tg[0] if tg else "NO"}\t{len(ex)}\t{",".join(ex) or "-"}\t{ru.ru_utime + ru.ru_stime:.1f}\t{w[0] if w else "-"}', flush=True)
