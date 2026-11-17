#!/usr/bin/env python3
"""exp3/analyze.py [T]: the deep runs (exp3/run.py) at T abstract s (default 320).
1. per arm: proved, gains and losses against C, CPU, peak memory, critical pairs to proof;
2. the stall replay (as stallsim.py, from each run's HINTLOG): proofs kept and work by stall limit;
3. the chain climb, for the arms with the chain (K, E, V): each HINTMATCHER rule, canonicalised as hint files
   are, is looked up in the chain; a chain hint's provenance is the nearest sibling whose expansion holds it
   (rank 0 = the sibling closest below the goal) and whether it is among that sibling's own proof steps.
   Reported for proved and unproved runs: matched chain hints, the share from rank 0-2, and the share of own
   steps matched per rank."""
import collections, os, re, sys
sys.path.insert(0, '/project/twee/hints')
import hintlib
T = sys.argv[1] if len(sys.argv) > 1 else '320'
os.chdir('/project/hintwork/exp3')
G = open('goals47').read().split()
R = {}
for a in 'CKEV':
    p = f'res_{a}@{T}.tsv'
    if os.path.exists(p):
        R[a] = {w[0]: w for w in (l.rstrip('\n').split('\t') for l in open(p))}
done = sorted(set.intersection(*[set(R[a]) for a in R])) if R else []
P = {a: {g for g in done if R[a][g][1] == '1'} for a in R}
print(f'{len(done)} goals done in all of {"".join(R)}')
for a in R:
    cpu = sum(float(R[a][g][2]) for g in done); mem = sorted(int(R[a][g][3]) for g in done)
    cps = sorted(int(R[a][g][4]) for g in P[a] if R[a][g][4]) or [0]
    print(f'  {a}: proved {len(P[a]):2d}  ' + ' '.join(f'vs {b} +{len(P[a]-P[b])} -{len(P[b]-P[a])}' for b in R if b != a) +
          f'  CPU {cpu/3600:.1f} h  peak MB median {mem[len(mem)//2] if mem else 0} max {mem[-1] if mem else 0}  CPs to proof median {cps[len(cps)//2]}')
# 2. stall replay
def hintlog(path):
    txt = open(path, errors='replace').read()
    m = re.search(r'^WORK considered=(\d+)', txt, re.M); work = int(m.group(1)) if m else None
    m = re.search(r'^HINTLOG(.*)$', txt, re.M); log = [int(x.split(':')[0]) for x in m.group(1).split()] if m else []
    return 'RESULT: Theorem' in txt, work, log
def stall_point(log, Gp, end):
    last = 0
    for c in log:
        if c - last > Gp: return last + Gp
        last = c
    return last + Gp if end - last > Gp else None
print('stall replay: proofs kept / work in abstract h, by stall limit (abstract s)')
gaps = [5, 10, 20, 40, 80, 160]
for a in R:
    runs = [hintlog(f'out_{a}@{T}/{g}') for g in done]
    row = []
    for gs in gaps + [None]:
        kept = work = 0
        for ok, w, log in runs:
            if w is None: continue
            sp = stall_point(log, gs * 2000, w) if gs else None
            if ok and (sp is None or w <= sp): kept += 1; work += w
            else: work += min(w, sp) if sp else w
        row.append(f'{gs or "none"}: {kept}/{work/2000/3600:.2f}')
    print(f'  {a}: ' + '  '.join(row))
    # when did the last new match come, proved vs not
    for lab, sel in (('proved', True), ('unproved', False)):
        L = sorted((log[-1] if log else 0) / 2000 for ok, w, log in runs if ok == sel and w)
        if L: print(f'     {lab}: last new match at median {L[len(L)//2]:.0f} abstract s (n {len(L)}, max {L[-1]:.0f})')
# 3. chain climb
S = {l.split('\t')[0]: [s for s in l.rstrip('\n').split('\t')[1].split(',') if s] for l in open('sibs10_47.tsv')}
own_n = {l.split('\t')[0]: int(l.split('\t')[5]) for l in open('xd.tsv') if not l.startswith('goal')}
def provenance(g):
    pv = {}
    for rk, s in enumerate(S[g]):
        try: L = open('xd/' + s).read().splitlines()
        except OSError: continue
        for i, x in enumerate(L):
            h = tuple(x.split('\t')[:2])
            if len(h) == 2 and h not in pv: pv[h] = (rk, i < own_n.get(s, 0))
    return pv
mre = re.compile(r'^HINTMATCHER \d+ (?:fof|cnf)\(\w+, axiom, (.*)\)\.\s*$')
def matchers(path, sig):
    out = set()
    for l in open(path, errors='replace'):
        m = mre.match(l)
        if not m: continue
        e = hintlib._split_eq(m.group(1))
        if e and e[0] != e[1]:
            out.add(min(hintlib.generalize(e[0], e[1], sig), hintlib.generalize(e[1], e[0], sig)))
    return out
print('chain climb: matched chain hints per run (median), share from siblings ranked 0-2, own steps of rank 0 matched')
for a in [x for x in 'KEV' if x in R]:
    for lab, sel in (('proved', True), ('unproved', False)):
        rows = []
        for g in done:
            if (g in P[a]) != sel: continue
            pv = provenance(g); sig = hintlib.problem_signature(g)
            M = [pv[k] for k in matchers(f'out_{a}@{T}/{g}', sig) if k in pv]
            own0 = sum(1 for k, v in pv.items() if v == (0, True)) or 1
            rows.append((len(M), sum(1 for rk, _ in M if rk <= 2) / max(len(M), 1), sum(1 for v in M if v == (0, True)) / own0))
        if rows:
            rows.sort(); n = len(rows); f = lambda i: sorted(r[i] for r in rows)[n // 2]
            print(f'  {a} {lab:8s} n {n:2d}: matched {f(0)}  rank 0-2 {f(1):.0%}  own steps of rank 0 matched {f(2):.0%}')
