#!/usr/bin/env python3
"""(22 Nov, exp58a; notes/2026-11-22-lemma-ax-replay.md) Replay a from-zero live given-rule loop's failed ancestry runs
with the source runs' lemma axioms named (givenmatch.lemma_ax), in the context the loop had at the time.

  gmreplay.py GML DST OUT [-j J] [--control N] [--seed S] -- TRANSFER_ARGS (the live loop's: $MOD --pool original ...)

GML is the live loop's dir (loops/Z8_GML), DST its loop (loops/Z8, from zero). The goals are those with an ancestry
(sketcha) run in GML/transfer.tsv and no proof there by any pass. For each, the context is DST's goals whose hint file
is older than the goal's sketch files (the time of the live loop's run), so the named lemma axioms are goals proven by
then. Arm 'lax': the same sketch files (copied), with lemma_ax applied. Arm 'ctl' (N goals, drawn with SEED): the
copies as they were, to check that the replay reproduces the live loop's failures. 20 s, --src-lemmas 6, as live.
Rows: OUT/replay.tsv (goal, arm, THM/NO, CPU s, named lemma axioms, run time, DST solve time or '').
"""
import os, random, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import givenmatch

a = sys.argv[1:]
rest = a[a.index('--') + 1:] if '--' in a else []
opts = a[:a.index('--')] if '--' in a else a
val = lambda k, d: type(d)(opts[opts.index(k) + 1]) if k in opts else d
gml, dst, out = (os.path.abspath(x) for x in opts[:3])
j, nctl, seed = val('-j', 1), val('--control', 0), val('--seed', 58)
os.makedirs(out)
runs = {}
for l in open(os.path.join(gml, 'transfer.tsv')):
    w = l.rstrip('\n').split('\t')
    runs.setdefault(w[0], []).append((w[1], w[4].split(',')))
G = sorted(g for g, r in runs.items() if any('/sketcha/' in fs[0] for _, fs in r) and not any(ok == 'THM' for ok, _ in r))
st = {}
for l in open(os.path.join(dst, 'solved.tsv')):
    g = l.split('\t')[0]
    p = os.path.join(dst, 'hints', g)
    if g not in st and os.path.exists(p):
        st[g] = os.path.getmtime(p)
order = sorted(st, key=st.get)
fsof = {g: next(fs for _, fs in runs[g] if '/sketcha/' in fs[0]) for g in G}
tof = {g: min(os.path.getmtime(f) for f in fsof[g]) for g in G}
ctl = set(random.Random(seed).sample(G, min(nctl, len(G))))
skroot = os.path.join(gml, 'sketcha')
jobs = []
for g in sorted(G, key=tof.get):   # (time order: lemma_ax's key index only grows)
    S = {m for m in order if st[m] < tof[g] and m != g}
    for arm in ('lax', 'ctl'):
        if arm == 'ctl' and g not in ctl:
            continue
        d = os.path.join(out, arm, g); sk = os.path.join(d, 'sk')
        nf = []
        for f in fsof[g]:
            rel = os.path.relpath(f, skroot)
            os.makedirs(os.path.dirname(os.path.join(sk, rel)), exist_ok=True)
            for x in (f, f + '.ax'):
                if os.path.exists(x):
                    shutil.copy2(x, os.path.join(sk, os.path.relpath(x, skroot)))
            nf.append(os.path.join(sk, rel))
        gp = os.path.join(d, 'goals.tsv')
        open(gp, 'w').write(f'{g}\t{",".join(nf)}\n')
        with open(os.path.join(d, 'solved.tsv'), 'w') as f:
            f.writelines(f'{m}\t0\t0\n' for m in sorted(S))
        os.symlink(os.path.join(dst, 'hints'), os.path.join(d, 'hints'))
        nax = 0
        if arm == 'lax':
            givenmatch.lemma_ax(gp, sk, S)
            nax = sum(1 for f in nf if os.path.exists(f + '.ax') for x in open(f + '.ax') if x.count('\t') >= 2)
        jobs.append((g, arm, d, gp, nax))
print(f'{len(G)} goals, {len(jobs)} runs ({len(ctl)} controls)', flush=True)
tp = os.path.join(os.path.dirname(givenmatch.__file__), 'transfer.py')
rf = open(os.path.join(out, 'replay.tsv'), 'a')


def one(jb):
    g, arm, d, gp, nax = jb
    with open(os.path.join(d, 'run.log'), 'w') as lf:
        subprocess.run([sys.executable, tp, 'run', gp, d, '-j', '1', '--time', '20', '--src-lemmas', '6', '--'] + rest,
                       stdout=lf, stderr=subprocess.STDOUT)
    w = (open(os.path.join(d, 'transfer.tsv')).readline().rstrip('\n').split('\t')
         if os.path.exists(os.path.join(d, 'transfer.tsv')) else [g, 'ERR', '0'])
    rf.write(f'{g}\t{arm}\t{w[1]}\t{w[2]}\t{nax}\t{time.strftime("%H:%M", time.gmtime(tof[g]))}\t'
             f'{time.strftime("%H:%M", time.gmtime(st[g])) if g in st else ""}\n')
    rf.flush()


with ThreadPoolExecutor(j) as ex:
    list(ex.map(one, jobs))
print('done', time.strftime('%T', time.gmtime()), flush=True)
