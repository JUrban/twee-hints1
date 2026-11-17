#!/usr/bin/env python3
"""exp4/nf.py GOALS OUT.tsv [-j J] [--time T] [--nf N] [--secs S]: subgoal conjectures by deduction from the goal.

For each goal, its captured production command (exp3/tb) runs with twee-e56 at T abstract s (default 20) with
--no-flatten-goal (flattening names the goal's subterms by constants, so the normal forms would be bare constants)
and --print-goal-nf N (default 3): on failure twee prints the N smallest normal forms of each side.
Each (left, right) pair of normal forms is decomposed: where the heads agree, f(u..) = f(v..) follows from the
u_i = v_i that differ. Every cut of that tree gives a sufficient set of subgoals; a set is kept when Mace4 finds
no countermodel to any of its subgoals in the real theory (sizes 2..12, S seconds, default 10). The goal's
constants are arbitrary, so each subgoal is the universal closure.
OUT.tsv: goal, set id, normal-form pair id, number of subgoals, screen ('ok' or the refuted subgoal), the
subgoals (; separated, LADR syntax with variables X0..). Twee outputs in OUT.d/."""
import argparse, concurrent.futures as cf, itertools, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moves import ladr, mace
_tok = re.compile(r"[A-Za-z0-9_]+|[(),]")
def parse(s):   # as in sketch.py
    toks = _tok.findall(s); i = 0
    def term():
        nonlocal i
        t = toks[i]; i += 1
        if i < len(toks) and toks[i] == '(':
            i += 1; args = []
            while True:
                args.append(term())
                if toks[i] == ',': i += 1
                else: i += 1; return (t, tuple(args))
        return (t, ())
    return term()
def show(t): return t[0] if not t[1] else f'{t[0]}({",".join(show(a) for a in t[1])})'
TB = '/project/hintwork/exp3/tb'
cmds = {}
for l in open(f'{TB}/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w

def nfs(g, T, od):
    w = list(cmds[g]); w[0] = '/project/bin/twee-e56'
    w[w.index('--max-time') + 1] = str(T); w[w.index('--max-cpu') + 1] = str(10 * T)
    w = [x for x in w if x != '--print-given'] + ['--no-flatten-goal', '--print-goal-nf', str(a.nf)]
    out = subprocess.run(w, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf8', 'replace')
    open(f'{od}/{g}', 'w').write(out)
    if 'HINTS-END' in out: return None
    side = {'L': [], 'R': []}
    for l in out.splitlines():
        m = re.match(r'GOALNF ([LR]) fof\(nf, axiom, (.*)\)\.$', l)
        if m:
            s = m.group(2).replace(' ', ''); side[m.group(1)].append(parse(s[:len(s) // 2]))
    return side

def cuts(s, t, budget=[0]):
    """sufficient subgoal sets for s = t: [(s,t)], or, where heads agree, a cut of each differing argument"""
    res = [[(s, t)]]
    if s[0] == t[0] and len(s[1]) == len(t[1]) and s[1]:
        d = [i for i in range(len(s[1])) if s[1][i] != t[1][i]]
        opts = [cuts(s[1][i], t[1][i])[:6] for i in d]
        for combo in itertools.islice(itertools.product(*opts), 30):
            res.append([p for part in combo for p in part])
    return res

def closure(pairs, consts):
    """the subgoals with the goal's constants as variables X0.. (in order of first occurrence)"""
    names = {}
    def gen(t):
        if not t[1] and t[0] in consts:
            names.setdefault(t[0], f'X{len(names)}'); return (names[t[0]], ())
        return (t[0], tuple(gen(x) for x in t[1]))
    return [f'{show(gen(s))} = {show(gen(t))}' for s, t in pairs]

def one(g):
    od = a.out + '.d'; side = nfs(g, a.time, od)
    if side is None: return [[g, '-', '-', 0, 'proved', '']]
    consts = set(re.findall(r'\b(x\d+)\b', ' '.join(show(t) for t in side['L'] + side['R'])))
    A, _ = ladr(g); rows, seen, cache = [], set(), {}
    for pi, (s, t) in enumerate(itertools.product(side['L'], side['R'])):
        for cut in cuts(s, t):
            # the subgoals as closed formulas, each closed on its own (a subgoal's constants are independent)
            subs = tuple(sorted(set(closure([p], consts)[0] for p in cut)))
            if subs in seen: continue
            seen.add(subs); bad = ''
            for c in subs:
                if c not in cache: cache[c] = mace(A, c, a.secs, end=12)
                if cache[c]: bad = c; break
            rows.append([g, len(rows), pi, len(subs), 'ok' if not bad else 'x ' + bad, '; '.join(subs)])
    return rows

ap = argparse.ArgumentParser(); ap.add_argument('goals'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=1); ap.add_argument('--time', type=float, default=20)
ap.add_argument('--nf', type=int, default=3); ap.add_argument('--secs', type=int, default=10)
a = ap.parse_args()
os.makedirs(a.out + '.d', exist_ok=True)
goals = [l.strip() for l in open(a.goals) if l.strip()]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for rows in ex.map(one, goals):
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
        f.flush()
