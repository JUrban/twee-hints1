#!/usr/bin/env python3
"""prec_replay.py CAPDIR OUT --goals FILE --orders FILE [-j J] [--cpu C] [--abstract T] (exp85, notes/2026-11-25-precedence-portfolio.md).

Reruns captured twee runs (exp/twee_capture.py: CAPDIR/log.jsonl, the first capture of each goal in FILE) under each
precedence of the orders file (`id<TAB>comma list`; an empty list is twee's default), with --max-cpu C in place of the
run's own cap, without --print-given/--print-given-unsolved/--print-hints, plus the captured TWEE_PG_ARGS. One row per
run in OUT: goal, order id, THM/NO, CPU s, wall s, critical pairs considered, rules (twee's WORK line). Goal by goal (all orders of a goal before the next); resumes OUT."""
import json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
A = sys.argv[1:]
def opt(k, d):
    return A[A.index(k) + 1] if k in A else d
CAP, OUT = A[0], A[1]
J, C = int(opt('-j', 4)), float(opt('--cpu', 10))
AT = opt('--abstract', '')
goals = [l.strip() for l in open(opt('--goals', '')) if l.strip()]
orders = [(l.split('\t')[0], l.rstrip('\n').split('\t')[1] if '\t' in l else '') for l in open(opt('--orders', '')) if l.strip()]
cap = {}
for l in open(os.path.join(CAP, 'log.jsonl')):
    r = json.loads(l)
    cap.setdefault(r['goal'], r)
done = set()
if os.path.exists(OUT):
    done = {tuple(l.split('\t')[:2]) for l in open(OUT)}
DROP = {'--print-given', '--print-given-unsolved', '--print-hints'}
def cmd(r, prec):
    a = [x for x in r['args'] if x not in DROP]
    i = a.index('--max-cpu') if '--max-cpu' in a else -1
    if i >= 0:
        a[i + 1] = str(C)
    else:
        a += ['--max-cpu', str(C)]
    if AT:   # (25 Nov) --abstract T: the run's limit in twee's abstract seconds (--max-time; 2000 considered critical
        j = a.index('--max-time') if '--max-time' in a else -1   # pairs each with --abstract-time 2000), deterministic;
        if j >= 0:                                                # --cpu is then only a safety cap
            a[j + 1] = AT
        else:
            a += ['--max-time', AT]
    if prec:
        a += ['--precedence', prec]
    return ['/project/bin/twee-e61'] + a + r['TWEE_PG_ARGS'].split()
lock = threading.Lock()
out = open(OUT, 'a')
def run(g, oid, prec):
    r = cap[g]
    t0 = time.time()
    p = subprocess.Popen(cmd(r, prec), cwd=r['cwd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    o = p.stdout.read().decode('utf8', 'replace')
    _, st, ru = os.wait4(p.pid, 0)
    p.returncode = st
    ok = 'RESULT: Theorem' in o
    # (25 Nov, the user: an order also dominates when it proves the same goals much faster) twee's abstract work,
    # the WORK line: critical pairs considered and rules, comparable across runs on a shared machine
    m = re.search(r'^WORK considered=(\d+) rules=(\d+)', o, re.M)
    wc, wr = (m.group(1), m.group(2)) if m else ('-', '-')
    with lock:
        out.write(f'{g}\t{oid}\t{"THM" if ok else "NO"}\t{ru.ru_utime + ru.ru_stime:.2f}\t{time.time() - t0:.2f}\t{wc}\t{wr}\n'); out.flush()
miss = [g for g in goals if g not in cap]
if miss:
    print('not captured:', len(miss), miss[:5], flush=True)
with ThreadPoolExecutor(J) as ex:
    fs = [ex.submit(run, g, oid, prec) for g in goals if g in cap for oid, prec in orders if (g, oid) not in done]
    print(f'{len(fs)} runs, -j {J}, --cpu {C}, --abstract {AT or "-"}', flush=True)
    for f in fs:
        f.result()
print('done', time.strftime('%d %T'), flush=True)
