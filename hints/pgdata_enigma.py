#!/usr/bin/env python3
"""Parental-guidance Pcat data on ENIGMA features (17 Nov; FroCoS 2021 section 3.3, Pcat + P_proof).

Reads twee-e52 --pg-log runs (RUN.err with PGR/PGN lines, RUN.out with PGPROOF lines), as pgdata.py, whose
labels it reuses: a pair (R, A) of a new rule R and an older or the same active A is positive when a proof
lemma came from it. PGR lines of e52 carry each rule's ENIGMA features in the rule model's c: vocabulary
(E<col>:<value>,...). Columns are renumbered in column order (as twee's PGEnigma):

  [0, C)        R's ENIGMA vector
  [C, 2C)       A's ENIGMA vector
  [2C, 2C+10)   R's pgRuleFeatures; [2C+10, 2C+20) A's; 2C+20 the id gap

usage: pgdata_enigma.py VOCAB OUT.npz RUN.err... [--neg N]   (OUT.npz: X as scipy CSR, y, n, run)
"""
import sys, random
import numpy as np, scipy.sparse as sp
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pgdata import proof_pairs


def vocab_rank(path):
    cols = sorted({int(l.split('\t')[0]) for l in open(path) if l.split('\t')[1].startswith('c:')})
    return {c: i for i, c in enumerate(cols)}


def load(err, rank):
    R, E, N, P = {}, {}, {}, set()
    for l in open(err, errors='replace'):
        if l.startswith('PGR '):
            w = l.rstrip('\n').split(' ', 7)
            f = None if w[5] == '-' else [float(x) for x in w[5].split(',')]
            e = None
            if w[6] != 'E-':
                e = {}
                for kv in w[6][1:].split(','):
                    if kv:
                        k, v = kv.split(':'); r = rank.get(int(k))
                        if r is not None:
                            e[r] = e.get(r, 0.0) + float(v)
            R[int(w[1])] = (int(w[2]), int(w[3]), f, w[7]); E[int(w[1])] = e
        elif l.startswith('PGN '):
            w = l.split()
            N[int(w[1])] = {int(k): int(v) for k, v in (x.split(':') for x in w[2:])}
    for l in open(err[:-4] + '.out', errors='replace'):
        if l.startswith('PGPROOF '):
            P.add(l.rstrip('\n')[8:])
    return R, E, N, P


def main():
    a = sys.argv[1:]
    neg = 0
    if '--neg' in a:
        i = a.index('--neg'); neg = int(a[i + 1]); del a[i:i + 2]
    rank = vocab_rank(a[0]); C = len(rank); out, errs = a[1], a[2:]
    rng = random.Random(1)
    data, ind, ptr = [], [], [0]
    y, w, run = [], [], []
    for k, err in enumerate(errs):
        R, E, N, P = load(err, rank)
        if not P:
            continue
        pos = proof_pairs(R, P)
        rows_p, rows_n = [], []
        for r, parts in N.items():
            if R.get(r, (0, 0, None))[2] is None or E.get(r) is None:
                continue
            for a_, n in parts.items():
                if R.get(a_, (0, 0, None))[2] is None or E.get(a_) is None:
                    continue
                (rows_p if (r, a_) in pos else rows_n).append((r, a_, n))
        if neg and len(rows_n) > neg * max(1, len(rows_p)):
            rows_n = rng.sample(rows_n, neg * max(1, len(rows_p)))
        for lab, rows in ((1, rows_p), (0, rows_n)):
            for r, a_, n in rows:
                fr, fa = R[r][2], R[a_][2]
                cols = sorted(E[r].items()) + [(C + c, v) for c, v in sorted(E[a_].items())]
                cols += [(2 * C + i, v) for i, v in enumerate(fr + fa + [fr[7] - fa[7]])]
                for c, v in cols:
                    ind.append(c); data.append(v)
                ptr.append(len(ind)); y.append(lab); w.append(n); run.append(k)
    X = sp.csr_matrix((np.array(data, dtype=np.float32), np.array(ind, dtype=np.int32), np.array(ptr, dtype=np.int64)),
                      shape=(len(y), 2 * C + 21))
    sp.save_npz(out + '.X.npz', X)
    np.savez_compressed(out, y=np.array(y, dtype=np.int8), n=np.array(w, dtype=np.int32), run=np.array(run, dtype=np.int32), C=C)
    print('%s: %d runs, %d rows, %d positive, %d columns' % (out, len(errs), len(y), sum(y), 2 * C + 21))


if __name__ == '__main__':
    main()
