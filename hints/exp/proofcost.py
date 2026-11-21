"""(21 Nov 23:58, notes/2026-11-21-proof-cost.md) Copy N queued proofq jobs (random, seed 8) and run each with the proof (proofq's command) and with --no-proof
(the search run's), sequentially; CPU from resource usage of the child."""
import glob, json, os, random, resource, shutil, subprocess, sys, time
S = sys.argv[1]; N = int(sys.argv[2])
dirs = ['Z7', 'Z7.xfer', 'Z7_GML', 'P2T', 'P2U', 'P2T.xfer']
random.seed(8)
picked = []
for d in dirs:
    js = sorted(glob.glob(f'/project/hintwork/loops/{d}/proofq/*/'))
    picked += [(d, j) for j in random.sample(js, min(len(js), N // len(dirs) + 1))]
rows = []
for k, (d, j) in enumerate(picked):
    j = j.rstrip('/')
    dst = f'{S}/jobs/{k}'
    try:
        shutil.copytree(j, dst)
        job = json.load(open(dst + '/job.json'))
    except Exception as e:
        continue
    jr = j.replace('/project/hintwork/', '')
    c = [x.replace(j, dst).replace(jr, dst) for x in job['cmd']]
    env = dict(os.environ, OMP_NUM_THREADS='1')
    if job.get('TWEE_PG_ARGS') is not None:
        env['TWEE_PG_ARGS'] = job['TWEE_PG_ARGS']
    res = {}
    for v, cc in (('proof', c), ('noproof', c + ['--no-proof'])):
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        p = subprocess.run(cc, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        out = p.stdout.decode('utf8', 'replace')
        cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
        res[v] = (cpu, 'RESULT: Theorem' in out, out)
    a, b = res['proof'][2], res['noproof'][2]
    i = a.find('The conjecture is true! Here is a proof.'); e = a.find('RESULT: Theorem', i)
    stripped = a[:i] + a[e:] if 0 <= i < e else a
    same = stripped.replace('\n', '') == b.replace('\n', '')
    T = c[c.index('--max-time') + 1] if '--max-time' in c else '?'
    rows.append((d, job['name'], T, res['proof'][0], res['noproof'][0], res['proof'][1], res['noproof'][1], same, len(a) - len(stripped)))
    print('\t'.join(map(str, rows[-1])), flush=True)
    shutil.rmtree(dst)
tp = sum(r[3] for r in rows); tn = sum(r[4] for r in rows)
print(f'jobs {len(rows)} proof-on CPU {tp:.1f} s, no-proof CPU {tn:.1f} s, extra {tp - tn:.1f} s ({100 * (tp - tn) / tn:.1f}%), '
      f'all proved both {all(r[5] and r[6] for r in rows)}, same output outside the proof {sum(r[7] for r in rows)}/{len(rows)}')
