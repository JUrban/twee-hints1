#!/usr/bin/env python3
"""exp1/analyze.py [T]: the exp1 arms (N none, O own steps, X expanded, P whole pool) at T abstract s (default 20):
proved, overlaps between arms, critical pairs to proof, and for each arm's proofs how many of their steps are not
in the original's pool (exp1/ph) and not in the goal's own lemma-based proof (loops/UL/hints)."""
import os, re, sys
T = sys.argv[1] if len(sys.argv) > 1 else '20'
os.chdir('/project/hintwork')
G = [l.strip() for l in open('exp1/s200') if l.strip()]
R = {}
for a in 'NOXP':
    p = f'exp1/r_{a}_{T}/results.tsv'
    if os.path.exists(p):
        R[a] = {w[0]: w for w in (l.rstrip('\n').split('\t') for l in open(p))}
def key(l, r): return (l, r) if l <= r else (r, l)
def hintset(p):
    try: return {tuple(x.split('\t')[:2]) for x in open(p).read().splitlines() if '\t' in x}
    except OSError: return set()
sys.path.insert(0, '/project/twee/hints')
import hintlib
def proof_steps(a, g):
    """the run's own proof steps (lemmas and goal lines), from --print-hints in its kept output"""
    p = f'exp1/r_{a}_{T}/out/{g}.out'
    if not os.path.exists(p): return None
    L, Gl = hintlib.extract_hints(open(p, errors='replace').read())
    sig = hintlib.problem_signature(g)
    ks = {min(hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig)) for l, r in L + Gl if l != r}
    return {k for k in ks if k[0] != k[1]}
done = set.intersection(*[set(R[a]) for a in R]) if R else set()
print(f'{len(done)} goals finished in all of {"".join(R)}')
for a in R:
    th = {g for g in done if R[a][g][1] == 'THM'}
    cps = sorted(int(R[a][g][3]) for g in th) if th else [0]
    print(f'{a}: proved {len(th)} of {len(done)}  median CPs to proof {cps[len(cps)//2]}  ' +
          '  '.join(f'vs {b}: +{len(th - {g for g in done if R[b][g][1]=="THM"})}' for b in R if b != a))
for a in R:
    tot = new_pool = new_own = n = 0
    for g in sorted(done):
        if R[a][g][1] != 'THM': continue
        s = proof_steps(a, g)
        if s is None: continue
        pool = hintset(f'exp1/ph/{g}'); own = hintset(f'loops/UL/hints/{g}')
        n += 1; tot += len(s); new_pool += len(s - pool); new_own += len(s - own)
    if n: print(f'{a}: {n} proofs, {tot/n:.0f} steps each; not in the pool {new_pool/max(tot,1):.0%}, not in own proof {new_own/max(tot,1):.0%}')
