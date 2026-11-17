#!/usr/bin/env python3
"""exp4/reinst.py SKETCH.tsv OUT.tsv [-j J] [--secs S] [--end N] [--cache R.tsv...]: the used instances of S,
extracted again from sketch.py's saved proofs (SKETCH.tsv.d/<goal>.<id>.out), and screened with Mace4 in T.

Fixes two faults of sketch.py's extraction (found 22:20):
* the instance is the redex of the step: the deepest position, on the path where the two terms differ, at which
  (before, after) is an instance of S (either orientation, one substitution for both sides). sketch.py took the
  innermost differing position, which for an argument filtering f(..X..) = f(..Y..) is inside the redex, so every
  filtering 'instance' came out as a false x = y;
* proof lines that are a bare variable are terms too.
Screen: sizes 2..N (default 12), S seconds (default 30). A countermodel found before (sketch.py's 5 s screen, or
rescreen.py's, given with --cache) is reused: either way the instance is false.
OUT.tsv: sketch.py's format, with columns 9-11 (instances, refuted, the instances, 'x ' marks refuted) redone."""
import argparse, concurrent.futures as cf, os, re, sys
sys.path.insert(0, '/project/twee/hints'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib
from moves import ladr, mace
_tok = re.compile(r"[A-Za-z0-9_]+|[(),]")
def parse(s):
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
def match(p, t, pv, sub):
    if not p[1] and p[0] in pv:
        if p[0] in sub: return sub[p[0]] == t
        sub[p[0]] = t; return True
    return p[0] == t[0] and len(p[1]) == len(t[1]) and all(match(x, y, pv, sub) for x, y in zip(p[1], t[1]))
def redex(a, b, pl, pr, pv):
    path = [(a, b)]
    while a[0] == b[0] and len(a[1]) == len(b[1]):
        d = [i for i in range(len(a[1])) if a[1][i] != b[1][i]]
        if len(d) != 1: break
        a, b = a[1][d[0]], b[1][d[0]]; path.append((a, b))
    for x, y in reversed(path):
        for l, r in ((pl, pr), (pr, pl)):
            s = {}
            if match(l, x, pv, s) and match(r, y, pv, s): return x, y
    return None
KEYW = ('Axiom', 'Lemma', 'Goal', 'Proof', 'RESULT', 'The conjecture', 'WORK', 'HINT', 'USED', 'CPULIMIT')
def instances(out):
    m = re.search(r'^Axiom (\d+) \(assume_S\): (.*) = (.*)\.$', out, re.M)
    if not m: return []
    ax, pl, pr = m.group(1), parse(m.group(2)), parse(m.group(3))
    pv = set(re.findall(r'\b[A-Z]\w*\b', m.group(2) + ' ' + m.group(3)))
    res, prev, pend = [], None, False
    for l in out.splitlines():
        s = l.strip()
        if s.startswith('= {'):
            pend = bool(re.match(rf'= {{ by axiom {ax} \(', s)); continue
        if not s or s.startswith(KEYW) or not re.match(r'^[A-Za-z]\w*(\(|$)', s) or '=' in s:
            prev = None; pend = False; continue
        t = parse(s)
        if pend and prev is not None:
            r = redex(prev, t, pl, pr, pv)
            if r: res.append((show(r[0]), show(r[1])))
        prev, pend = t, False
    return res
ap = argparse.ArgumentParser(); ap.add_argument('sketch'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=3); ap.add_argument('--secs', type=int, default=30)
ap.add_argument('--end', type=int, default=12); ap.add_argument('--cache', nargs='*', default=[])
a = ap.parse_args()
known = {}   # (goal, instance) -> refuted?
for p in a.cache:
    for l in open(p):
        w = l.rstrip('\n').split('\t')
        if w[2] != '-': known[(w[0], w[1])] = True
rows = [l.rstrip('\n').split('\t') for l in open(a.sketch)]
for r in rows:
    for x in r[10].split('; ') if len(r) > 10 else []:
        if x.startswith('x '): known[(r[0], x[2:])] = True
todo, per_row = [], []
for r in rows:
    inst = []
    if r[4] == '1' and r[5] == '1':
        sig = hintlib.problem_signature(r[0]); seen = set()
        for l, rr in instances(open(f'{a.sketch}.d/{r[0]}.{r[1]}.out', errors='replace').read()):
            k = min(hintlib.generalize(l, rr, sig), hintlib.generalize(rr, l, sig))
            if k in seen or k[0] == k[1]: continue
            seen.add(k); c = f'{k[0]} = {k[1]}'; inst.append(c)
            if (r[0], c) not in known and (r[0], c) not in todo: todo.append((r[0], c))
    per_row.append(inst)
print(len(todo), 'instances to screen', flush=True)
def one(p):
    A, _ = ladr(p[0]); return p, mace(A, p[1], a.secs, end=a.end) is not None
with cf.ThreadPoolExecutor(a.j) as ex:
    for p, bad in ex.map(one, todo): known[p] = bad
with open(a.out, 'w') as f:
    for r, inst in zip(rows, per_row):
        if r[4] == '1' and r[5] == '1':
            marked = [('x ' if known.get((r[0], c)) else '') + c for c in inst]
            r = r[:8] + [str(len(inst)), str(sum(m.startswith('x ') for m in marked)), '; '.join(marked)]
        f.write('\t'.join(r) + '\n')
