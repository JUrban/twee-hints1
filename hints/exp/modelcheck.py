#!/usr/bin/env python3
"""(20 Nov 11:00) Soundness audit by finite models: every proof step must hold in every model of its theory.

After the p9twee negation bug (notes/2026-11-20-p9-negation-bug.md) the trust fixpoint only covers that one bug. This
is an independent check of every proof in production. For each theory (an original's axiom set), Mace4 finds up to
--models models of sizes 2..8. Each step of every solved unit goal's proof (production's hints file) is evaluated
there under every assignment of its variables. A step false in some model of the axioms is not a theorem, so the
proof that logged it is not a proof. The steps of conditional goals' proofs may use the hypothesis, so those are
skipped.
Self-test: every goal statement of AIM60k is a theorem (a step of a real proof), so each must hold in every model;
a failure there means a wrong model or a wrong evaluator, not a wrong proof.

  modelcheck.py OUTDIR [-j 4] [--models 40] [--goals all|solved] [--max-cells 2000000]
writes OUTDIR/models/<theory>.out (Mace4), OUTDIR/false_steps.tsv (goal, step line, l, r, model) and
OUTDIR/false_goals.tsv (the self-test's failures), and prints a summary.
"""
import collections, hashlib, os, re, subprocess, sys
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, '/project/twee/hints')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lemmas, p9twee
from gensat import unit
from joincheck import parse

L = '/project/hintwork/loops'
OUT = None
NMOD = 40
MAXC = 2_000_000


def theory_key(ax):
    return hashlib.sha1('\n'.join(sorted(ax)).encode()).hexdigest()[:16]


def mace(args):
    key, ax, out = args
    p = os.path.join(out, 'models', key + '.out')
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return key
    inp = ('set(prolog_style_variables).\nassign(start_size,2).\nassign(end_size,8).\n'
           f'assign(max_models,{NMOD}).\nassign(max_seconds,120).\nformulas(assumptions).\n'
           + ''.join(p9twee.ladr(a) + '.\n' for a in ax) + 'end_of_list.\n')
    open(p + '.in', 'w').write(inp)
    r = subprocess.run(['/project/bin/mace4', '-f', p + '.in'], capture_output=True, text=True, timeout=600)
    open(p + '.tmp', 'w').write(r.stdout)
    os.replace(p + '.tmp', p)
    return key


def read_models(p):
    """Mace4 output -> [(n, {symbol: (arity, flat table)})]"""
    txt = open(p).read()
    out = []
    for m in re.finditer(r'interpretation\(\s*(\d+),\s*\[[^\]]*\],\s*\[(.*?)\]\)\.', txt, re.S):
        n = int(m.group(1))
        fs = {}
        for f in re.finditer(r'function\(\s*([A-Za-z0-9_]+)(\(([_,]*)\))?\s*,\s*\[([^\]]*)\]\s*\)', m.group(2)):
            ar = 0 if not f.group(2) else f.group(3).count('_')
            fs[f.group(1)] = (ar, np.array([int(x) for x in f.group(4).replace('\n', ' ').split(',')], dtype=np.int64))
        out.append((n, fs))
    return out


def ev(t, n, fs, vix, nv):
    """the term's value over the grid n^nv (variable i on axis i), as a broadcastable array"""
    if isinstance(t, str):
        sh = [1] * nv
        sh[vix[t]] = n
        return np.arange(n, dtype=np.int64).reshape(sh)
    ar, tab = fs[t[0]]
    if ar == 0:
        return np.int64(tab[0])
    args = [ev(a, n, fs, vix, nv) for a in t[1:]]
    idx = np.int64(0)
    for a in args:
        idx = idx * n + a
    return tab[idx]


def vars_of(t, acc):
    if isinstance(t, str):
        if t not in acc:
            acc.append(t)
    else:
        for a in t[1:]:
            vars_of(a, acc)
    return acc


def syms(t, acc):
    if not isinstance(t, str):
        acc.add(t[0])
        for a in t[1:]:
            syms(a, acc)
    return acc


def holds(l, r, M):
    """None if it holds in every model (or none could check it), else the index of a model where it fails"""
    vs = vars_of(r, vars_of(l, []))
    S = syms(r, syms(l, set()))
    for i, (n, fs) in enumerate(M):
        if not S <= fs.keys() or n ** max(len(vs), 1) > MAXC:
            continue
        vix = {v: k for k, v in enumerate(vs)}
        a = ev(l, n, fs, vix, len(vs)); b = ev(r, n, fs, vix, len(vs))
        if not np.all(a == b):
            return i
    return None


def check_theory(args):
    """one theory: the self-test on its goals, then the steps of its solved unit goals"""
    key, goals, solved = args
    M = read_models(os.path.join(OUT, 'models', key + '.out'))
    if not M:
        return key, 0, [], [], 0, 0
    bad_goals, bad_steps = [], []
    memo = {}
    nsteps = nskip = 0
    for g in goals:
        u = unit(g)
        if not u:
            continue
        try:
            l, r = parse(u[1]), parse(u[2])
        except (AssertionError, IndexError):
            continue
        i = holds(l, r, M)
        if i is not None:
            bad_goals.append((g, u[1], u[2], i))
    for g in solved:
        if not unit(g):
            continue
        try:
            lines = open(os.path.join(L, 'UL', 'hints', g)).read().split('\n')
        except OSError:
            continue
        for k, x in enumerate(lines):
            w = x.split('\t')
            if len(w) < 2:
                continue
            kk = (w[0], w[1])
            if kk not in memo:
                try:
                    memo[kk] = holds(parse(w[0]), parse(w[1]), M)
                except (AssertionError, IndexError, KeyError):
                    memo[kk] = 'skip'
            v = memo[kk]
            if v == 'skip':
                nskip += 1
                continue
            nsteps += 1
            if v is not None:
                bad_steps.append((g, k, w[0], w[1], v))
    return key, len(M), bad_goals, bad_steps, nsteps, nskip


def main():
    global OUT, NMOD, MAXC
    a = sys.argv[1:]
    OUT = os.path.abspath(a[0])
    j = int(a[a.index('-j') + 1]) if '-j' in a else 4
    NMOD = int(a[a.index('--models') + 1]) if '--models' in a else 40
    MAXC = int(a[a.index('--max-cells') + 1]) if '--max-cells' in a else MAXC
    os.makedirs(os.path.join(OUT, 'models'), exist_ok=True)
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    by_o = collections.defaultdict(list)
    for g in names:
        by_o[lemmas.split(g)[0]].append(g)
    th = {}
    for o, gs in by_o.items():
        ax = p9twee.tptp_parts(gs[0])[0]
        k = theory_key(ax)
        th.setdefault(k, [ax, []])[1].extend(gs)
    print(f'{len(by_o)} originals, {len(th)} theories', flush=True)
    with Pool(j) as pool:
        for k in pool.imap_unordered(mace, [(k, v[0], OUT) for k, v in th.items()]):
            pass
    print('models ready', flush=True)
    tot = collections.Counter()
    fg = open(os.path.join(OUT, 'false_goals.tsv'), 'w')
    fs_ = open(os.path.join(OUT, 'false_steps.tsv'), 'w')
    with Pool(j) as pool:
        for key, nm, bg, bs, ns, nk in pool.imap_unordered(
                check_theory, [(k, v[1], [g for g in v[1] if g in S]) for k, v in th.items()]):
            tot['models'] += nm; tot['steps'] += ns; tot['skipped'] += nk
            tot['false goals'] += len(bg); tot['false steps'] += len(bs)
            tot['theories without models'] += nm == 0
            for g, l, r, i in bg:
                fg.write(f'{g}\t{l}\t{r}\t{key}:{i}\n')
            for g, k, l, r, i in bs:
                fs_.write(f'{g}\t{k}\t{l}\t{r}\t{key}:{i}\n')
            fg.flush(); fs_.flush()
            print(f'  {key}: {nm} models, {ns} steps, {len(bg)} false goals, {len(bs)} false steps', flush=True)
    bad = sorted({l.split('\t')[0] for l in open(os.path.join(OUT, 'false_steps.tsv'))})
    # (20 Nov 12:37) the alarm: a false step with the same variables on both sides is the shape of a wrong derived
    # equation (the printed goal terms have different variables on the two sides; notes/2026-11-20-model-audit.md)
    alarm = []
    for l in open(os.path.join(OUT, 'false_steps.tsv')):
        w = l.rstrip('\n').split('\t')
        if set(re.findall(r'X\d+', w[2])) == set(re.findall(r'X\d+', w[3])):
            alarm.append(l)
    open(os.path.join(OUT, 'alarm.tsv'), 'w').writelines(alarm)
    if alarm:
        print(f'ALARM: {len(alarm)} false steps with the same variables on both sides, in '
              f'{len({l.split(chr(9))[0] for l in alarm})} goals (OUTDIR/alarm.tsv)', flush=True)
    open(os.path.join(OUT, 'false_step_goals.txt'), 'w').writelines(g + '\n' for g in bad)
    print('modelcheck: ' + ', '.join(f'{v} {k}' for k, v in tot.items()) + f'; {len(bad)} goals with a false step',
          flush=True)


if __name__ == '__main__':
    main()
