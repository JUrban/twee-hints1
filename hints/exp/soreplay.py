#!/usr/bin/env python3
"""(22 Nov 13:31, exp58b; notes/2026-11-22-src-used.md) Replay a from-zero live loop's failed same-statement runs
with transfer.py --src-used (the lemma axioms the source proofs used, named by their goals), in the loop's context at
the time.

  soreplay.py GML DST OUT [-j J] [--sample N] [--control K] [--seed S] -- TRANSFER_ARGS (the live loop's)

The goals: those with a failed same-statement run in GML/transfer.tsv (sources are goal names, not sketch files) and
no proof by any of its passes; N of them drawn with SEED, K of those also run unchanged ('ctl'). The context of a
goal is DST's goals whose hint file is older than the first so_*.tsv file listing it. DST/proofs holds the source
proofs' texts (exp/proofq.py). 20 s, --src-lemmas 6, as live. Rows: OUT/replay.tsv (goal, arm, THM/NO, CPU s, lemma
axioms added, run time, DST solve time or '').
"""
import glob, os, random, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lemmas, transfer

a = sys.argv[1:]
rest = a[a.index('--') + 1:] if '--' in a else []
opts = a[:a.index('--')] if '--' in a else a
val = lambda k, d: type(d)(opts[opts.index(k) + 1]) if k in opts else d
gml, dst, out = (os.path.abspath(x) for x in opts[:3])
j, nsam, nctl, seed = val('-j', 1), val('--sample', 100), val('--control', 20), val('--seed', 58)
os.makedirs(out)
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(gml, 'transfer.tsv'))]
thm = {w[0] for w in rows if w[1] == 'THM'}
src = {}
for w in rows:
    if '/sketch' not in w[4] and w[1] != 'THM' and w[0] not in thm:
        src.setdefault(w[0], w[4].split(','))
first = {}
for f in sorted(glob.glob(os.path.join(gml, 'so_*.tsv')), key=os.path.getmtime):
    for l in open(f):
        first.setdefault(l.split('\t')[0], os.path.getmtime(f))
G = sorted(g for g in src if g in first)
rnd = random.Random(seed)
sam = sorted(rnd.sample(G, min(nsam, len(G))))
ctl = set(rnd.sample(sam, min(nctl, len(sam))))
st = {}
for l in open(os.path.join(dst, 'solved.tsv')):
    g = l.split('\t')[0]
    p = os.path.join(dst, 'hints', g)
    if g not in st and os.path.exists(p):
        st[g] = os.path.getmtime(p)
jobs = []
for g in sorted(sam, key=first.get):
    S = {m for m in st if st[m] < first[g] and m != g}
    for arm in ('used', 'ctl'):
        if arm == 'ctl' and g not in ctl:
            continue
        d = os.path.join(out, arm, g)
        os.makedirs(d)
        gp = os.path.join(d, 'goals.tsv')
        open(gp, 'w').write(f'{g}\t{",".join(src[g])}\n')
        with open(os.path.join(d, 'solved.tsv'), 'w') as f:
            f.writelines(f'{m}\t0\t0\n' for m in sorted(S))
        os.symlink(os.path.join(dst, 'hints'), os.path.join(d, 'hints'))
        n = 0
        if arm == 'used':
            os.makedirs(os.path.join(d, 'proofs'))   # (only the source proofs, linked: a proofq rerun writes here)
            A, seen = lemmas.axiom_set(g), set()
            for s_ in src[g]:
                pf = os.path.join(dst, 'proofs', s_)
                if os.path.exists(pf):
                    os.symlink(pf, os.path.join(d, 'proofs', s_))
                    for m in transfer.used_lemma_goals(open(pf).read(), lemmas.split(s_)[0]):
                        if m != g and m in S and m not in seen and lemmas.axiom_set(m) <= A:
                            seen.add(m)
            n = len(seen)
        jobs.append((g, arm, d, gp, n))
print(f'{len(G)} goals, sample {len(sam)}, {len(jobs)} runs ({len(ctl)} controls)', flush=True)
tp = transfer.__file__
rf = open(os.path.join(out, 'replay.tsv'), 'a')


def one(jb):
    g, arm, d, gp, n = jb
    with open(os.path.join(d, 'run.log'), 'w') as lf:
        subprocess.run([sys.executable, tp, 'run', gp, d, '-j', '1', '--time', '20', '--src-lemmas', '6']
                       + (['--src-used'] if arm == 'used' else []) + ['--'] + rest, stdout=lf, stderr=subprocess.STDOUT)
    p = os.path.join(d, 'transfer.tsv')
    w = open(p).readline().rstrip('\n').split('\t') if os.path.exists(p) else [g, 'ERR', '0']
    rf.write(f'{g}\t{arm}\t{w[1]}\t{w[2]}\t{n}\t{time.strftime("%H:%M", time.gmtime(first[g]))}\t'
             f'{time.strftime("%H:%M", time.gmtime(st[g])) if g in st else ""}\n')
    rf.flush()


with ThreadPoolExecutor(j) as ex:
    list(ex.map(one, jobs))
print('done', time.strftime('%T', time.gmtime()), flush=True)
