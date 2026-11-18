#!/usr/bin/env python3
"""exp6/run.py CMDS ARM J [EXTRA...]: the ground-joining limit test. CMDS: lines 'id<TAB>command' (full twee
command lines). Each command is run with the EXTRA twee arguments appended, under a wall limit of 1.5 x its
--max-cpu + 60 s (the run is then KILLED). Writes res_<ARM>.tsv: id, proved, CPU s, peak MB, considered pairs,
end (ok = normal end, CPULIMIT, KILLED, HEAP), wall s."""
import concurrent.futures as cf, re, subprocess, sys, time
cmds_f, arm, J, extra = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
jobs = [l.rstrip('\n').split('\t') for l in open(cmds_f) if l.strip()]
done = set()
try: done = {l.split('\t')[0] for l in open(f'res_{arm}.tsv')}
except OSError: pass
def run(job):
    i, cmd = job; w = cmd.split() + extra
    cap = float(w[w.index('--max-cpu') + 1])
    t0 = time.time()
    p = subprocess.Popen(['/usr/bin/time', '-f', 'TIME %U %S %M'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=1.5 * cap + 60); killed = False
    except subprocess.TimeoutExpired:
        subprocess.run(['pkill', '-KILL', '-P', str(p.pid)])   # first the twee child of /usr/bin/time (by parent PID)
        out, err = p.communicate(); killed = True
    out = out.decode('utf8', 'replace'); err = err.decode('utf8', 'replace')
    m = re.search(r'TIME ([\d.]+) ([\d.]+) (\d+)', err)
    cpu, mem = (float(m.group(1)) + float(m.group(2)), int(m.group(3)) // 1024) if m else (time.time() - t0, 0)
    ok = 'HINTS-END' in out
    if ok:   # (18 Nov 07:50) proved runs keep their output (for tomerge.py), without the given log
        import os
        os.makedirs(f'out_{arm}', exist_ok=True)
        gi, gj = out.find('GIVEN-BEGIN'), out.find('GIVEN-END')
        open(f'out_{arm}/{i}', 'w').write(out[:gi] + out[gj:] if 0 <= gi < gj else out)
    c = re.search(r'WORK considered=(\d+)', out)
    end = 'KILLED' if killed else 'HEAP' if 'Heap exhausted' in out + err else 'CPULIMIT' if 'CPULIMIT' in out else 'ok' if c else 'other'
    return i, int(ok), f'{cpu:.1f}', mem, c.group(1) if c else '', end, f'{time.time() - t0:.0f}'
with cf.ThreadPoolExecutor(J) as ex, open(f'res_{arm}.tsv', 'a') as f:
    for r in ex.map(run, [j for j in jobs if j[0] not in done]):
        f.write('\t'.join(map(str, r)) + '\n'); f.flush()
