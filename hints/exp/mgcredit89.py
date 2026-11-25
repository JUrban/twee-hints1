"""(25 Nov, exp89) credit an extra goal proved in a multi-goal replay (exp/multigoal89.py): rerun the same problem
(OUT/<target>.mg.p, deterministic under --abstract-time) with the proof and hints printed, to just past the extra's
SOLVEDGOAL, and write a loop record for merge.py: DIR/solved.tsv (round 1), DIR/hints/<extra> (the proof's steps,
canonical as loop.py writes them), DIR/out/<extra> (the kept output, for trust.py), DIR/proofs/<extra>.
Usage: mgcredit89.py TARGET EXTRA PAIRS MGDIR DIR"""
import json, os, re, subprocess, sys, time
sys.path.insert(0, '/project/twee/hints')
import hintlib, loop
tg, ex, pairs, mgd, D = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
r = [json.loads(l) for l in open('/project/hintwork/loops/P85C/cap/log.jsonl') if json.loads(l)['goal'] == tg][-1]
a = list(r['args']); src = next(x for x in a if x.endswith('.p'))
pp = os.path.join(mgd, tg + '.mg.p')
T = str(-(-pairs // 2000) + 1)   # abstract s just past the SOLVEDGOAL
drop = {'--print-given', '--print-given-unsolved', '--no-proof', '--quiet'}
cmd = []; i = 0
while i < len(a):
    if a[i] in drop: i += 1; continue
    if a[i] in ('--max-time', '--max-cpu'): i += 2; continue
    if a[i] == src: cmd.append(pp); i += 1; continue
    cmd.append(a[i]); i += 1
cmd = ['/project/bin/twee-e61'] + cmd + ['--max-time', T, '--max-cpu', '3000', '--multi-goal'] + r['TWEE_PG_ARGS'].split()
t0 = time.time()
out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=r['cwd']).stdout
dt = time.time() - t0
sg = [l for l in out.splitlines() if l.startswith('SOLVEDGOAL ')]
print('\n'.join(sg)); print([l for l in out.splitlines() if l.startswith(('RESULT', 'WORK', 'USEDAXIOMS'))])
assert any(l.split()[1] == 'mg_' + ex for l in sg), 'extra not proved'
assert not any(l.split()[1] == 'goals' for l in sg), 'the target was proved too: its proof would be mixed in'
L, G = hintlib.extract_hints(out)
sig = hintlib.problem_signature(ex)
seen, hs = set(), []
for l, rr in L + G:
    if l == rr: continue
    k = loop.canon_key(l, rr, sig)
    if k[0] == k[1] or k in seen: continue
    seen.add(k); hs.append(k)
os.makedirs(os.path.join(D, 'hints'), exist_ok=True); os.makedirs(os.path.join(D, 'out'), exist_ok=True)
os.makedirs(os.path.join(D, 'proofs'), exist_ok=True)
open(os.path.join(D, 'hints', ex), 'w').writelines('\t'.join(k) + '\n' for k in hs)
hdr = f'% exp89 (exp/mgcredit89.py): {ex} proved as an extra goal of {tg}\'s multi-goal replay\n% command: {" ".join(cmd)}\n'
open(os.path.join(D, 'out', ex), 'w').write(hdr + out)
open(os.path.join(D, 'proofs', ex), 'w').write(hdr + out)
with open(os.path.join(D, 'solved.tsv'), 'a') as f:
    f.write(f'{ex}\t1\t{dt:.2f}\n')
print(ex, len(hs), 'hints, %.0f s' % dt)
