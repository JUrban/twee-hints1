#!/usr/bin/env python3
"""(20 Nov 10:25) Which of production's proofs are trusted (exp/unsound.py's records, as a fixpoint).

A proof is trusted if it is older than T0 (15 Nov 08:56, the first unsound Prover9 proof in production), or if a
record names every lemma it used (a kept twee output's USEDAXIOMS, a climber's used.tsv) and each of those is a
trusted proven goal. Anything else (no record, a lemma name that is not resolved: srclem_, skax_, an unnamed
lemma_knn_I, ...) is untrusted. Production's proofs are written to OUT.untrusted for quarantine.

  trust.py OUT [-j 4]

The rest of this docstring is unsound.py's:

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


def read_out(pd):
    """(goal, dir, [used names], mtime) for a kept twee output that proved its goal, else None"""
    p, d = pd
    try:
        with open(p, errors='replace') as f:
            txt = f.read()
        mt = os.path.getmtime(p)
    except OSError:
        return None
    if 'RESULT: Theorem' not in txt:
        return None
    m = re.search(r'^USEDAXIOMS (.*)$', txt, re.M)
    return os.path.basename(p), d, m.group(1).split() if m else None, mt


def main():
    import time
    out = sys.argv[1]
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 4
    T0 = time.mktime(time.strptime('2026-11-15 08:56', '%Y-%m-%d %H:%M'))
    S = {l.split('\t')[0] for l in open(os.path.join(L, 'UL', 'solved.tsv'))}
    S = {g for g in S if os.path.exists(os.path.join(L, 'UL', 'hints', g))}
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
    # (20 Nov 11:21) also one level down (loops/REVER2/p1/r1/out: rever2's passes), with the dir the output belongs
    # to (its hints dir decides whether the output made production's proof)
    ods = set()
    for d in dirs:
        for pat in (('r*', 'out'), ('out',), ('*', 'r*', 'out'), ('*', 'out')):
            ods.update(glob.glob(os.path.join(L, d, *pat)))
    for od in sorted(ods):
        dd = os.path.relpath(os.path.dirname(od), L)
        if re.fullmatch(r'r\d+', os.path.basename(dd)):
            dd = os.path.dirname(dd)   # (DIR/rN/out belongs to DIR)
        paths.extend((os.path.join(od, x), dd) for x in os.listdir(od))
    print(f'{len(paths)} kept outputs in {len(dirs)} dirs', flush=True)
    rec = {}    # goal -> set of lemma goals, or None if a used lemma name is not resolved
    knn_at = {}

    def resolve(g, d, x):
        """a used axiom name -> a goal name, '' for the problem's own axioms and conjecture, None if unresolved"""
        m = re.match(r'(?:lemma|assume)_goal_(\d+)$', x)
        if m:
            return f'{orig(g)}__goal_{m.group(1)}'
        m = re.match(r'(?:lemma|assume)_knn_\d+_(.+__goal_\d+)$', x) or re.match(r'srclem_\d+_(.+__goal_\d+)$', x) \
            or re.match(r'skax_\d+_(.+__goal_\d+)$', x)
        if m:
            return m.group(1)
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
            lst = knn_at[d].get(g); i = int(m.group(1))
            return lst[i] if lst and i < len(lst) else None
        if x.startswith(('lemma', 'assume', 'srclem', 'skax', 'hint_axiom', 'p9lemma', 'true', 'fill', 'gen', 'cut')):
            return None
        return ''
    def add(g, d, names):
        deps = set()
        for x in names:
            r = resolve(g, d, x)
            if r is None:
                deps = None
                break
            if r:
                deps.add(r)
        if g in rec and rec[g] is not None and deps is not None:
            rec[g] = rec[g] | deps
        elif g not in rec:
            rec[g] = deps
    # (20 Nov 11:21) each goal's record from its newest output that matches production's hints: the side loops'
    # hints dirs are symlinks to production's, so an old proof of a goal since re-proved also "matches"
    newest = {}
    with Pool(j) as pool:
        for r in pool.imap_unordered(read_out, paths, chunksize=500):
            if r is None:
                continue
            g, d, names, mt = r
            if g in S and same(d, g) and (g not in newest or mt > newest[g][0]):
                newest[g] = (mt, d, names)
    for g, (mt, d, names) in newest.items():
        if names is not None:
            add(g, d, names)
    for p in glob.glob(os.path.join(L, '*', 'used.tsv')):
        d = p.split('/')[-2]
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 3 and w[0] in S and same(d, w[0]):
                add(w[0], d, [x for x in w[2].split(',') if x])
    old = {g for g in S if os.path.getmtime(os.path.join(L, 'UL', 'hints', g)) < T0}
    trusted = set(old)
    if '--exposed' in sys.argv:
        # (20 Nov 10:36) every lemma mechanism takes lemmas from theories within the target's (siblings, kNN with subsets,
        # proof-dependency sets, transfer's srclem guard and .ax from runs of weaker theories, the climber's true
        # lemmas, the base lemmas), so a proof can rest on a bad goal only if its theory contains the bad goal's:
        # outside the EXPOSED originals every proof is trusted, record or not
        ex = {l.strip() for l in open(sys.argv[sys.argv.index('--exposed') + 1]) if l.strip()}
        safe = {g for g in S if orig(g) not in ex}
        print(f'{len(safe - trusted)} later proofs outside the {len(ex)} exposed originals', flush=True)
        trusted |= safe
    changed = True
    while changed:
        changed = False
        for g in S - trusted:
            deps = rec.get(g)
            if deps is not None and g in rec and deps <= trusted:
                trusted.add(g); changed = True
    un = sorted(S - trusted)
    norec = sum(1 for g in un if g not in rec)
    unres = sum(1 for g in un if g in rec and rec[g] is None)
    open(out + '.untrusted', 'w').writelines(g + '\n' for g in un)
    # (20 Nov 12:07) what each untrusted proof with a complete record waits for: its lemmas not trusted
    with open(out + '.missing', 'w') as f:
        for g in un:
            if rec.get(g):
                f.write(f'{g}\t{",".join(sorted(rec[g] - trusted))}\n')
    open(out + '.trusted', 'w').writelines(g + '\n' for g in sorted(trusted))
    # roots: untrusted for want of a record (none, or a lemma name not resolved), not for an untrusted lemma
    open(out + '.roots', 'w').writelines(g + '\n' for g in un if g not in rec or rec[g] is None)
    print(f'{len(S)} solved: {len(old)} before T0, {len(trusted) - len(old)} later with trusted records; '
          f'{len(un)} untrusted ({norec} without a record, {unres} with an unresolved lemma name, '
          f'{len(un) - norec - unres} using an untrusted or unsolved lemma)', flush=True)


if __name__ == '__main__':
    main()
