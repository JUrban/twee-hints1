#!/usr/bin/env python3
"""Parental-guidance training data from twee --pg-log runs (17 Nov).

Each run's stderr has PGR lines (id, parents, raw score, features of 'pgRuleFeatures', canonical rule)
and PGN lines (a new rule's critical pairs per partner); its stdout PGPROOF lines (the proof's lemmas,
canonical). A pair (R, A) of a new rule R and an older or the same active A is positive when some proof
lemma came from it (FroCoS 2021 P_proof: parents of proof clauses), otherwise negative. Only pairs of
two rules with features count: the others are always made.

Row = twee's pgPairFeatures: R's 10 features, A's 10, R.id - A.id; then label, overlaps, run.

usage: pgdata.py OUT.npz RUN.err... (RUN.out next to each RUN.err) [--neg N: at most N negatives per
positive in each run, sampled at random; 0 = all]
"""
import sys, random, collections
import numpy as np


def load(err):
    R, N, P = {}, {}, set()
    for l in open(err, errors='replace'):
        if l.startswith('PGR '):
            w = l.rstrip('\n').split(' ', 6)
            f = None if w[5] == '-' else [float(x) for x in w[5].split(',')]
            R[int(w[1])] = (int(w[2]), int(w[3]), f, w[6])
        elif l.startswith('PGN '):
            w = l.split()
            N[int(w[1])] = {int(k): int(v) for k, v in (x.split(':') for x in w[2:])}
    for l in open(err[:-4] + '.out', errors='replace'):
        if l.startswith('PGPROOF '):
            P.add(l.rstrip('\n')[8:])
    return R, N, P


def proof_pairs(R, P):
    first = {}
    for i in sorted(R):
        first.setdefault(R[i][3], i)
    pos = set()
    for c in P:
        i = first.get(c)
        if i is None:
            continue
        p1, p2 = R[i][0], R[i][1]
        if p1 and p2:
            pos.add((max(p1, p2), min(p1, p2)))
    return pos


def rows(err, neg, rng):
    R, N, P = load(err)
    if not P:
        return []
    pos = proof_pairs(R, P)
    out_pos, out_neg = [], []
    for r, parts in N.items():
        fr = R.get(r, (0, 0, None, ''))[2]
        if fr is None:
            continue
        for a, n in parts.items():
            fa = R.get(a, (0, 0, None, ''))[2]
            if fa is None:
                continue
            x = fr + fa + [fr[7] - fa[7]]
            (out_pos if (r, a) in pos else out_neg).append((x, n))
    if neg and len(out_neg) > neg * max(1, len(out_pos)):
        out_neg = rng.sample(out_neg, neg * max(1, len(out_pos)))
    return [(x, 1, n) for x, n in out_pos] + [(x, 0, n) for x, n in out_neg]


def main():
    a = sys.argv[1:]
    neg = 0
    if '--neg' in a:
        i = a.index('--neg'); neg = int(a[i + 1]); del a[i:i + 2]
    out, errs = a[0], a[1:]
    rng = random.Random(1)
    X, y, w, run = [], [], [], []
    for k, e in enumerate(errs):
        for x, lab, n in rows(e, neg, rng):
            X.append(x); y.append(lab); w.append(n); run.append(k)
    X = np.array(X, dtype=np.float32); y = np.array(y, dtype=np.int8)
    np.savez_compressed(out, X=X, y=y, n=np.array(w, dtype=np.int32), run=np.array(run, dtype=np.int32),
                        runs=np.array(errs))
    print('%s: %d runs, %d rows, %d positive' % (out, len(errs), len(y), int(y.sum())))


if __name__ == '__main__':
    main()
