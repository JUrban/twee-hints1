#!/usr/bin/env python3
"""exp4/sketch.py MOVES.tsv OUT.tsv [-j J] [--time T]: sketch runs for the moves that moves.py kept ('ok').

Each run is the goal's captured production command (exp3/tb: sibling and kNN lemmas, the original's pool, rm4t,
twee-e48, PG 0.25) at T abstract s (default 5), with the proof printed, and
  an up move S: the problem plus fof(assume_S, axiom, S);
  a weaker goal: the conjecture replaced by the instance.
For a proof of an up move: whether S was used (USEDAXIOMS), the proof's size (lemmas printed as hints), and
the instances of S the proof used: at each step 'by axiom k (assume_S)' the two terms differ at one position,
the redex; (redex = contractum), with the goal's constants generalised to variables, is the instance. Each
instance is screened with Mace4 in the real theory (a countermodel up to size 8 in 5 s = false).
OUT.tsv: goal, move id, kind, move, proved, S used, proof lemmas, CPU s, instances used, of them refuted, the
instances (; separated, 'x' marks a refuted one). Outputs in OUT.d/<goal>.<id>."""
import argparse, concurrent.futures as cf, os, re, subprocess, sys
sys.path.insert(0, '/project/twee/hints'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib
from moves import ladr, mace
TB = '/project/hintwork/exp3/tb'
cmds = {}
for l in open(f'{TB}/cmds.all'):
    w = l.split(); cmds[os.path.basename(w[1])[:-2]] = w
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
def redex(a, b):
    """the subterms at the one position where a and b differ"""
    while a != b:
        if a[0] == b[0] and len(a[1]) == len(b[1]):
            d = [i for i in range(len(a[1])) if a[1][i] != b[1][i]]
            if len(d) == 1: a, b = a[1][d[0]], b[1][d[0]]; continue
        return a, b
    return None
def instances(out, ax_no):
    """(lhs, rhs) strings of the steps 'by axiom ax_no' in twee's printed proof"""
    res, prev, pend = [], None, False
    for l in out.splitlines():
        s = l.strip()
        if s.startswith('= {'):
            pend = bool(re.match(rf'= {{ by axiom {ax_no} \(', s)); continue
        if not s or s.startswith(('Axiom', 'Lemma', 'Goal', 'Proof', 'RESULT', 'The conjecture', 'WORK', 'HINT')):
            prev = None; pend = False; continue
        if re.match(r'^[a-z]\w*(\(|$)', s) and '=' not in s:
            t = parse(s)
            if pend and prev is not None:
                r = redex(prev, t)
                if r: res.append((show(r[0]), show(r[1])))
            prev, pend = t, False
    return res
def run(row, T):
    g, mid, kind, mv = row[:4]
    w = list(cmds[g]); prob = open(w[1]).read()
    os.makedirs(f'{a.out}.d', exist_ok=True); pp = f'{a.out}.d/{g}.{mid}.p'
    if kind == 'inst':
        body = mv.strip().rstrip('.').strip()
        vs = sorted(set(re.findall(r'\bX\d+\b', body)))
        conj = f"fof(goals,conjecture,{'! [' + ','.join(vs) + '] : ' if vs else ''}{body})."
        prob = re.sub(r'fof\(goals,conjecture,.*?\)\.\s*$', conj, prob, flags=re.M | re.S)
    else:
        vs = sorted(set(re.findall(r'\b[A-H]\b', mv)))
        prob += f"\nfof(assume_S,axiom,{'! [' + ','.join(vs) + '] : ' if vs else ''}{mv}).\n"
    open(pp, 'w').write(prob)
    w[1] = pp; w[w.index('--max-time') + 1] = str(T); w[w.index('--max-cpu') + 1] = str(10 * T)
    w = [x for x in w if x not in ('--no-proof', '--print-given')]
    p = subprocess.run(['/usr/bin/time', '-f', '%U %S'] + w, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cpu = sum(float(x) for x in p.stderr.decode().strip().split('\n')[-1].split())
    out = p.stdout.decode('utf8', 'replace'); open(f'{a.out}.d/{g}.{mid}.out', 'w').write(out)
    ok = 'RESULT: Theorem' in out
    used = bool(re.search(r'^USEDAXIOMS.*\bassume_S\b', out, re.M))
    L, _ = hintlib.extract_hints(out) if ok else ([], [])
    inst, bad = [], 0
    if ok and used:
        m = re.search(r'^Axiom (\d+) \(assume_S\)', out, re.M)
        sig = hintlib.problem_signature(g)
        seen = set()
        for l, r in instances(out, m.group(1)) if m else []:
            k = min(hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig))
            if k in seen or k[0] == k[1]: continue
            seen.add(k)
            A, _G = ladr(g)
            c = mace(A, f'{k[0]} = {k[1]}', 5)
            bad += c is not None; inst.append(('x ' if c else '') + f'{k[0]} = {k[1]}')
    return [g, mid, kind, mv, int(ok), int(used), len(L), f'{cpu:.1f}', len(inst), bad, '; '.join(inst)]
ap = argparse.ArgumentParser(); ap.add_argument('moves'); ap.add_argument('out')
ap.add_argument('-j', type=int, default=2); ap.add_argument('--time', type=float, default=5)
a = ap.parse_args()
rows = [l.rstrip('\n').split('\t') for l in open(a.moves)]
rows = [r for r in rows if r[4] == 'ok' and r[0] in cmds]
with cf.ThreadPoolExecutor(a.j) as ex, open(a.out, 'a') as f:
    for res in ex.map(lambda r: run(r, a.time), rows):
        f.write('\t'.join(map(str, res)) + '\n'); f.flush()
