#!/usr/bin/env python3
"""(20 Nov 09:50) The production proofs that rest on the 13 unsound Prover9 proofs, transitively.

p9twee.ladr wrote TPTP '~ a = b' as LADR '- a = b', which Prover9 reads as the equation (-a) = b with '-' a
function symbol: every conditional sibling lemma became a false axiom (fixed 20 Nov 09:45). 13 of the side Prover9
loops' proofs (loops/P9C, P9L, P9T) used such a clause; their goals are true statements (AIM60k's goals are steps of
real proofs), but our proofs of them are not proofs. A later proof that used one of them as a lemma axiom is a proof
modulo an unproved lemma. This finds them, to a fixpoint, from:
  * kept twee outputs (loops/*/r*/out/<goal>, loops/*/out/<goal>) with 'RESULT: Theorem': USEDAXIOMS names
    lemma_goal_J (the goal's original's goal J), lemma_knn_I_<goal>; lemma_knn_I without a name is resolved through
    the dir's knn_at.tsv when it has the goal, else counted as unresolved;
  * the transfer loops' transfer.tsv (THM rows: every goal named in the sources column, conservatively);
  * the climbers' used.tsv (every lemma_* and assume_goal_* name of the target's rows, conservatively).
A record counts for production's proof of G only if it is production's own (loops/UL) or the dir's hints file of G
is production's, byte for byte.

  unsound.py BAD.txt OUT.txt [-j 4]     (BAD: one goal per line; OUT: the closure, with the reason per goal)
"""
import collections, glob, os, re, sys
from multiprocessing import Pool

L = '/project/hintwork/loops'
FROMZERO = re.compile(r'^(Z\d|PG[A-Z]|P2[A-Z]|OR[A-Z]|UA|UB|SMT|ABa|ABb|ABc|ABd|ABe)$')
GOAL = re.compile(r'[A-Za-z0-9_]+__goal_\d+')


def orig(g):
    return g.rsplit('__goal_', 1)[0]


def read_out(p):
    """(goal, dir, [used names]) for a kept twee output that proved its goal, else None"""
    try:
        with open(p, errors='replace') as f:
            txt = f.read()
    except OSError:
        return None
    if 'RESULT: Theorem' not in txt:
        return None
    m = re.search(r'^USEDAXIOMS (.*)$', txt, re.M)
    parts = p.split('/')
    return os.path.basename(p), parts[parts.index('loops') + 1], m.group(1).split() if m else None


def main():
    bad0 = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    out = sys.argv[2]
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 4
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    ulh = {}

    def same(d, g):
        if d == 'UL':
            return True
        try:
            if g not in ulh:
                ulh[g] = open(os.path.join(L, 'UL', 'hints', g), 'rb').read()
            return open(os.path.join(L, d, 'hints', g), 'rb').read() == ulh[g]
        except OSError:
            return False
    dirs = [d for d in os.listdir(L) if os.path.isdir(os.path.join(L, d)) and not FROMZERO.match(d)]
    paths = []
    for d in dirs:
        for od in glob.glob(os.path.join(L, d, 'r*', 'out')) + glob.glob(os.path.join(L, d, 'out')):
            paths.extend(os.path.join(od, x) for x in os.listdir(od))
    print(f'{len(paths)} kept outputs in {len(dirs)} dirs', flush=True)
    dep = collections.defaultdict(set)      # goal -> lemma goals its production proof may have used
    why = collections.defaultdict(set)
    unres = collections.defaultdict(set)   # goal -> dirs with an unresolved lemma_knn_I
    knn_at = {}
    with Pool(j) as pool:
        for r in pool.imap_unordered(read_out, paths, chunksize=500):
            if r is None:
                continue
            g, d, names = r
            if g not in S or names is None or not same(d, g):
                continue
            for x in names:
                m = re.match(r'lemma_goal_(\d+)$', x)
                if m:
                    dep[g].add(f'{orig(g)}__goal_{m.group(1)}'); why[g].add(d); continue
                m = re.match(r'lemma_knn_(\d+)_(.+__goal_\d+)$', x)
                if m:
                    dep[g].add(m.group(2)); why[g].add(d); continue
                m = re.match(r'lemma_knn_(\d+)$', x)
                if m:
                    if d not in knn_at:
                        knn_at[d] = {}
                        p = os.path.join(L, d, 'knn_at.tsv')
                        if os.path.exists(p):
                            for l in open(p):
                                w = l.rstrip('\n').split('\t')
                                if len(w) >= 2:
                                    knn_at[d][w[0]] = w[1].split(',')
                    lst = knn_at[d].get(g)
                    i = int(m.group(1))
                    if lst and i < len(lst):
                        dep[g].add(lst[i]); why[g].add(d + ':knn_at')
                    else:
                        unres[g].add(d)
    for p in glob.glob(os.path.join(L, '*', 'transfer.tsv')):
        d = p.split('/')[-2]
        if FROMZERO.match(d):
            continue
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 5 and w[1] == 'THM' and w[0] in S and same(d, w[0]):
                for x in GOAL.findall(w[4]):
                    if x != w[0]:
                        dep[w[0]].add(x)
                why[w[0]].add(d + ':transfer')
    for p in glob.glob(os.path.join(L, '*', 'used.tsv')):
        d = p.split('/')[-2]
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 3 and w[0] in S and same(d, w[0]):
                for x in w[2].split(','):
                    m = re.match(r'(?:lemma|assume)_goal_(\d+)$', x)
                    if m:
                        dep[w[0]].add(f'{orig(w[0])}__goal_{m.group(1)}')
                    m = re.match(r'(?:lemma|assume)_knn_\d+_(.+__goal_\d+)$', x)
                    if m:
                        dep[w[0]].add(m.group(1))
                why[w[0]].add(d + ':used')
    D = {g: 'unsound Prover9 proof' for g in bad0}
    changed = True
    while changed:
        changed = False
        for g, ls in dep.items():
            if g not in D:
                hit = sorted(ls & D.keys())
                if hit:
                    D[g] = f'uses {hit[0]}' + (f' (+{len(hit) - 1})' if len(hit) > 1 else ''); changed = True
    with open(out, 'w') as f:
        for g in sorted(D):
            f.write(f'{g}\t{D[g]}\n')
    nrec = len(dep)
    print(f'{nrec} production proofs with lemma records; closure {len(D)} goals ({len(D) - len(bad0)} besides the '
          f'{len(bad0)}); {len(unres)} proofs with an unresolved kNN lemma; {len(S) - nrec} solved goals without a '
          f'record', flush=True)
    open(out + '.records', 'w').writelines(f'{g}\t{",".join(sorted(why[g]))}\n' for g in sorted(dep))
    near = sorted(g for g in unres if g not in D)
    open(out + '.unresolved', 'w').writelines(f'{g}\t{",".join(sorted(unres[g]))}\n' for g in near)


if __name__ == '__main__':
    main()
