#!/usr/bin/env python3
"""(20 Nov 12:12) Semantic guidance, offline (Slaney's SCOTT, Lusk-McCune's and Slaney et al.'s semantic guidance in
Otter; notes/2026-11-20-semantic-guidance.md): are proof steps false in a 'relevance model' more often than the other
given rules?

Every original is the 17 base axioms (loops with the inner-mapping definitions and AIM) plus 0-11 extra axioms. A
relevance model is a finite model of the base in which some extra axiom fails (Mace4: assumptions the base, goal the
conjunction of the extras). A rule derived in the full theory that is false in such a model depends on the extras.
The hypothesis: proofs need the extras, so their steps are enriched in such rules, and a rule's falsity there is a
guidance feature twee's syntactic rule model does not see.

For each original with extras: up to --models relevance models (sizes 2..8). For up to --logs given logs of its
proved goals (loops/UL/given: -1 axiom, 0 a given rule not in the proof, 1 a proof step): each rule's falsity in some
model. Prints per original and in total: proof steps false / all, other rules false / all, the lift.

  semguide.py OUTDIR [--logs 10] [--models 10] [-j 2] [--seed 1]
"""
import collections, os, random, re, subprocess, sys
from multiprocessing import Pool
sys.path.insert(0, '/project/twee/hints')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lemmas, p9twee
import modelcheck as mc
from joincheck import parse

L = '/project/hintwork/loops'
OUT = None
NM = 10
NL = 10
SEED = 1


def base_axioms(all_ax):
    cnt = collections.Counter(a for s in all_ax.values() for a in s)
    return {a for a, c in cnt.items() if c >= 100}


def relmodels(args):
    o, base, extra = args
    p = os.path.join(OUT, 'models', o + '.out')
    if not os.path.exists(p):
        inp = ('set(prolog_style_variables).\nassign(start_size,2).\nassign(end_size,8).\n'
               f'assign(max_models,{NM}).\nassign(max_seconds,30).\nformulas(assumptions).\n'
               + ''.join(p9twee.ladr(a) + '.\n' for a in sorted(base)) + 'end_of_list.\nformulas(goals).\n'
               + ' & '.join('(' + p9twee.ladr(a) + ')' for a in sorted(extra)) + '.\nend_of_list.\n')
        open(p + '.in', 'w').write(inp)
        r = subprocess.run(['/project/bin/mace4', '-f', p + '.in'], capture_output=True, text=True, timeout=900)
        open(p + '.tmp', 'w').write(r.stdout)
        os.replace(p + '.tmp', p)
    return o, len(mc.read_models(p))


def study(args):
    o, logs = args
    M = mc.read_models(os.path.join(OUT, 'models', o + '.out'))
    if not M:
        return o, 0, None
    memo = {}
    c = collections.Counter()
    for g in logs:
        for x in open(os.path.join(L, 'UL', 'given', g)):
            w = x.rstrip('\n').split('\t')
            if len(w) < 4 or w[0] not in ('0', '1'):
                continue
            k = (w[2], w[3])
            if k not in memo:
                try:
                    memo[k] = mc.holds(parse(w[2]), parse(w[3]), M) is not None
                except (AssertionError, IndexError, KeyError):
                    memo[k] = None
            v = memo[k]
            if v is None:
                continue
            lab = 'pos' if w[0] == '1' else 'neg'
            c[lab] += 1
            c[lab + '_false'] += v
    return o, len(M), c


def main():
    global OUT, NM, NL, SEED
    a = sys.argv[1:]
    def val(k, d):
        return type(d)(a[a.index(k) + 1]) if k in a else d
    OUT = os.path.abspath(a[0]); NM = val('--models', 10); NL = val('--logs', 10); SEED = val('--seed', 1)
    j = val('-j', 2)
    mc.MAXC = 500_000
    os.makedirs(os.path.join(OUT, 'models'), exist_ok=True)
    names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
    by = collections.defaultdict(list)
    for g in names:
        by[lemmas.split(g)[0]].append(g)
    ax = {o: set(p9twee.tptp_parts(gs[0])[0]) for o, gs in by.items()}
    base = base_axioms(ax)
    todo = [(o, ax[o] & base, ax[o] - base) for o in sorted(ax) if ax[o] - base]
    print(f'{len(ax)} originals, {len(base)} base axioms, {len(todo)} with extras', flush=True)
    with Pool(j) as pool:
        nm = dict(pool.imap_unordered(relmodels, todo))
    print(f'relevance models: {sum(1 for v in nm.values() if v)} originals have some '
          f'({sum(nm.values())} models)', flush=True)
    have = set(os.listdir(os.path.join(L, 'UL', 'given')))
    rnd = random.Random(SEED)
    jobs = []
    for o, _, _ in todo:
        if not nm.get(o):
            continue
        gs = sorted(g for g in by[o] if g in have)
        rnd.shuffle(gs)
        if gs:
            jobs.append((o, gs[:NL]))
    T = collections.Counter()
    rows = []
    with Pool(j) as pool:
        for o, n, c in pool.imap_unordered(study, jobs):
            if c is None:
                continue
            T.update(c)
            pf = c['pos_false'] / max(c['pos'], 1); nf = c['neg_false'] / max(c['neg'], 1)
            rows.append((o, n, c['pos'], pf, c['neg'], nf))
            print(f'  {o}: {n} models; proof steps {c["pos_false"]}/{c["pos"]} false ({pf:.1%}), '
                  f'other given rules {c["neg_false"]}/{c["neg"]} ({nf:.1%})', flush=True)
    open(os.path.join(OUT, 'per_original.tsv'), 'w').writelines(
        f'{o}\t{n}\t{p}\t{pf:.4f}\t{q}\t{nf:.4f}\n' for o, n, p, pf, q, nf in sorted(rows))
    pf = T['pos_false'] / max(T['pos'], 1); nf = T['neg_false'] / max(T['neg'], 1)
    # P(proof step | false) / P(proof step | true)
    pt = (T['pos'] - T['pos_false']); nt = (T['neg'] - T['neg_false'])
    lift = (T['pos_false'] / max(T['pos_false'] + T['neg_false'], 1)) / max(pt / max(pt + nt, 1), 1e-9)
    print(f'semguide: {len(rows)} originals; proof steps false {T["pos_false"]}/{T["pos"]} ({pf:.1%}), other given '
          f'rules {T["neg_false"]}/{T["neg"]} ({nf:.1%}); P(step|false)/P(step|true) = {lift:.2f}', flush=True)


if __name__ == '__main__':
    main()
