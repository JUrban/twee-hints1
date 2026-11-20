#!/usr/bin/env python3
"""(20 Nov 15:05; the user: search with --no-proof, rerun a proved run with the proof printed, keep the proofs)
The proof worker. loop.py queues every proved twee run in DIR/proofq/<job>/ (job.json: the command without
--no-proof and --dump-state, its files hard-linked into the job dir; loop.py proof_job). This reruns each job, cuts
the proof from 'The conjecture is true! Here is a proof.' to the RESULT line into DIR/proofs/<goal> (and into the
live destination's proofs/, e.g. loops/UL/proofs, for transfer runs), logs DIR/proofq.log, and removes the job.
Twee is deterministic for a given command (with --abstract-time also under load), so the rerun finds the same
proof; a rerun that does not is logged as NOPROOF.

  proofq.py [--follow] [-j 1] [--poll 30] [--root /project/hintwork/loops]
--follow: keep polling (every --poll seconds) for new jobs, under ROOT/*/proofq and ROOT/*/*/proofq.
"""
import glob, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

B, E = 'The conjecture is true! Here is a proof.', 'RESULT: Theorem (the conjecture is true).'
lock = threading.Lock()


def block(t):
    i = t.find(B)
    j = t.find(E, i)
    return t[i:j + len(E)] + '\n' if 0 <= i < j else None


def write(d, name, text):
    pd = os.path.join(d, 'proofs')
    os.makedirs(pd, exist_ok=True)
    tmp = os.path.join(pd, f'.{name}.{os.getpid()}.{threading.get_ident()}')
    with open(tmp, 'w') as f:
        f.write(text)
    os.replace(tmp, os.path.join(pd, name))


def run(jd):
    try:
        job = json.load(open(os.path.join(jd, 'job.json')))
    except (OSError, ValueError):
        return
    env = dict(os.environ, OMP_NUM_THREADS='1')
    if job.get('TWEE_PG_ARGS') is not None:
        env['TWEE_PG_ARGS'] = job['TWEE_PG_ARGS']
    c = job['cmd']
    T = float(c[c.index('--max-time') + 1]) if '--max-time' in c else 60.0
    t0 = time.time()
    try:
        p = subprocess.run(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=20 * T + 120)
        out = p.stdout.decode('utf8', 'replace')
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b'').decode('utf8', 'replace')
    dt = time.time() - t0
    b = block(out)
    if b:
        write(job['dir'], job['name'], b)
        if job.get('dst') and os.path.isdir(job['dst']):
            write(job['dst'], job['name'], b)
    with lock:
        with open(os.path.join(job['dir'], 'proofq.log'), 'a') as f:
            f.write(f'{time.strftime("%d %H:%M:%S")}\t{job["name"]}\t{"PROOF" if b else "NOPROOF"}\t{dt:.2f}\n')
    for f in job.get('files', []) + ['job.json']:   # (only the job's own files, then its dir)
        try:
            os.unlink(os.path.join(jd, f))
        except OSError:
            pass
    try:
        os.rmdir(jd)
    except OSError:
        pass


def jobs(root):
    js = []
    for pat in (os.path.join(root, '*', 'proofq', '*'), os.path.join(root, '*', '*', 'proofq', '*')):
        js.extend(x for x in glob.glob(pat) if not x.endswith('.tmp') and os.path.isdir(x))
    return sorted(set(js), key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0)


def main():
    a = sys.argv[1:]
    def val(k, d):
        return type(d)(a[a.index(k) + 1]) if k in a else d
    j, poll, root = val('-j', 1), val('--poll', 30.0), val('--root', '/project/hintwork/loops')
    follow = '--follow' in a
    busy = set()
    with ThreadPoolExecutor(j) as ex:
        while True:
            new = [x for x in jobs(root) if x not in busy]
            for x in new:
                busy.add(x)
                ex.submit(run, x).add_done_callback(lambda f, x=x: busy.discard(x))
            if not follow:
                break
            time.sleep(poll)
            while len(busy) > 4 * j:   # (do not run ahead of the pool with a long listing)
                time.sleep(1)


if __name__ == '__main__':
    main()
