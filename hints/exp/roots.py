#!/usr/bin/env python3
"""(21 Nov 00:55) Which of production's proofs a from-zero run was one proof away from (notes/2026-11-21-roots.md).

For the goals production (loops/UL) proved and ARM did not: each goal's lemma record (exp/trust.py --dump-rec: the
lemma goals named by the newest kept output that made production's proof). A goal is a root if every lemma it
used is a goal ARM proved (or it used none): ARM had the context for that proof. The reach is the fixpoint: goals
whose lemmas are all in ARM or reached. A root's descendants are the reached goals that have it among their
ancestors (transitively, through the lemma records within the gap).

  roots.py REC.tsv ARM [--set SET] [--out ROOTS.tsv]
Columns of ROOTS.tsv: root, first production label (results.tsv column 5 of its first THM row, else the side
writer's dir), that row's seconds, number of lemmas, descendants.
"""
import collections, glob, os, sys

L = '/project/hintwork/loops'


def solved(d):
    return {l.split('\t')[0] for l in open(f'{L}/{d}/solved.tsv') if l.strip()}


def main():
    a = sys.argv[1:]
    def val(k, d):
        if k in a:
            i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
        return d
    st, out = val('--set', None), val('--out', None)
    rp, arm = a[0], a[1]
    H = {l.strip() for l in open(st) if l.strip()} if st else None
    U, Z = solved('UL'), solved(arm)
    if H is not None:
        U, Z = U & H, Z & H
    G = U - Z
    rec = {}
    for l in open(rp):
        w = l.rstrip('\n').split('\t')
        if len(w) == 2:
            rec[w[0]] = w[1]
    lab = {}
    for p in sorted(glob.glob(f'{L}/UL/r*/results.tsv')):
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5 and w[1] == 'THM' and w[0] in G and w[0] not in lab:
                lab[w[0]] = ('V*' if w[4].startswith('V') else w[4], w[2])
    for p in glob.glob(f'{L}/*/transfer.tsv'):
        d = p.split('/')[-2]
        for l in open(p, errors='replace'):
            w = l.split('\t')
            if len(w) >= 3 and w[1] == 'THM' and w[0] in G and w[0] not in lab:
                lab[w[0]] = (d, w[2])
    st_ = collections.Counter()
    deps = {}
    for g in G:
        r = rec.get(g, 'NOREC')
        if r in ('NOREC', 'UNRES'):
            st_[r] += 1
            continue
        deps[g] = set(r.split(',')) if r else set()
        st_['record'] += 1
    print(f'{arm}: {len(Z)} proved; production {len(U)}; production only {len(G)}: '
          + ', '.join(f'{k} {v}' for k, v in st_.most_common()))
    roots = {g for g, d in deps.items() if d <= Z}
    order, R = [], set()
    changed = True
    while changed:
        changed = False
        for g in sorted(deps):
            if g not in R and deps[g] <= Z | R:
                R.add(g); order.append(g); changed = True
    # (00:58) why the rest are not reached: through the unreached lemmas (transitively) a gap goal without a record,
    # a lemma production did not prove, or neither (a cycle: the newest outputs of re-proved goals use later lemmas)
    out_set = collections.Counter()
    for g, d in deps.items():
        if g in R:
            continue
        seen, todo, kind = set(), [g], set()
        while todo:
            x = todo.pop()
            for y in deps.get(x, ()):
                if y in Z or y in R or y in seen:
                    continue
                seen.add(y)
                if y not in U:
                    kind.add('nu')
                elif y not in deps:
                    kind.add('norec')
                else:
                    todo.append(y)
        out_set['a chain to a gap goal without a record' if 'norec' in kind else
                'a chain to a lemma production did not prove' if 'nu' in kind else 'a cycle only'] += 1
    print(f'roots {len(roots)}; reach {len(R)} of the {len(deps)} with a record; not reached: '
          + ', '.join(f'{k} {v}' for k, v in out_set.most_common()))
    c = collections.Counter(lab.get(g, ('unknown', ''))[0] for g in roots)
    print('roots by first production label: ' + ', '.join(f'{k} {v}' for k, v in c.most_common(15)))
    c2 = collections.Counter(lab.get(g, ('unknown', ''))[0] for g in G)
    print('production only by first label: ' + ', '.join(f'{k} {v}' for k, v in c2.most_common(15)))
    anc = {}
    for g in order:
        s = set()
        for x in deps[g]:
            if x in G:
                s.add(x); s |= anc.get(x, set())
        anc[g] = s
    desc = collections.Counter()
    for g in R:
        for x in anc[g]:
            desc[x] += 1
    rows = sorted(roots, key=lambda g: -desc[g])
    tot = sum(1 for g in R if g not in roots)
    acc, k50 = 0, None
    cov = set()
    for i, g in enumerate(rows):
        cov |= {h for h in R if g in anc[h]}
        if k50 is None and len(cov) >= tot / 2:
            k50 = i + 1
    print(f'reached non-roots {tot}; {k50} roots (by descendants) are ancestors of half of them')
    nd = collections.Counter(min(desc[g], 10) for g in roots)
    print('roots by descendants (10 = 10 or more): ' + ', '.join(f'{k}:{nd[k]}' for k in sorted(nd)))
    for g in rows[:25]:
        lb, sec = lab.get(g, ('unknown', ''))
        print(f'  {g}\t{lb}\t{sec}\t{len(deps[g])} lemmas\t{desc[g]} descendants')
    if out:
        with open(out, 'w') as f:
            for g in rows:
                lb, sec = lab.get(g, ('unknown', ''))
                f.write(f'{g}\t{lb}\t{sec}\t{len(deps[g])}\t{desc[g]}\n')


if __name__ == '__main__':
    main()
