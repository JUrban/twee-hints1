#!/usr/bin/env python3
"""(20 Nov 10:25) Which of production's proofs are trusted (exp/unsound.py's records, as a fixpoint).

A proof is trusted if it is older than T0 (15 Nov 08:56, the first unsound Prover9 proof in production), or if a
record names every lemma it used (a kept twee output's USEDAXIOMS, a climber's used.tsv) and each of those is a
trusted proven goal. Anything else (no record, a lemma name that is not resolved: srclem_, skax_, an unnamed
lemma_knn_I, ...) is untrusted. Production's proofs are written to OUT.untrusted for quarantine.

  trust.py OUT [-j 4] [--exposed EXPOSED.txt] [--dump-rec REC.tsv]

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
        mu = os.path.getmtime(p)
        # (23 Nov) the climber's own real proofs (its solved.tsv rows of round 1): the record is the target's LAST
        # used.tsv row, the run that made the real proof (climb.py: an assumption-free sketch proof ends the climb,
        # else the final run, then 'direct'). The earlier rows are sketch proofs with assume_* axioms; the real proof
        # only took their steps as hints, so they are not its premises. (Before, every row counted and any assume_*
        # made the record unresolved: no climber proof in an exposed original could be trusted.)
        own = set()
        if os.path.exists(os.path.join(L, d, 'climb.tsv')) and os.path.exists(os.path.join(L, d, 'solved.tsv')):
            own = {l.split('\t')[0] for l in open(os.path.join(L, d, 'solved.tsv')) if l.split('\t')[1:2] == ['1']}
        # (20 Nov 13:38) when production's hints file is newer than the whole used.tsv, that proof has since been
        # replaced (CLHL2 stopped at 10:04; its old rows kept REVER4's sound re-proofs of mbol_12lemmas 526 and three
        # more untrusted through a quarantined lemma). Only for a dir whose hints are production's (a symlink: live
        # climbers); a dir with its own hints (set mode, merged with merge.py, which copies the file later than the
        # rows) is matched by same()'s byte comparison
        link = os.path.islink(os.path.join(L, d, 'hints'))
        last = {}
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) < 3 or w[0] not in S or not same(d, w[0]) or \
                    (link and os.path.getmtime(os.path.join(L, 'UL', 'hints', w[0])) > mu):
                continue
            if w[0] in own:
                last[w[0]] = w
            else:
                add(w[0], d, [x for x in w[2].split(',') if x])
        for g, w in last.items():
            add(g, d, [x for x in w[2].split(',') if x])
    # (23 Nov) fill lemmas (climb.py --fill: a gap of a sketch proved on its own, a true lemma of the original). Each
    # is a node FILL:<dir>:<original>:<true label>, with a record from the dir's fillprem.tsv (written since 23 Nov
    # 23:03: the lemma names the fill run's proofs used; true_k is another fill lemma of the same dir). A formula's
    # node FORM:<original>:<formula> is trusted when any of its fill lemmas is. A climber's real proof names its fill
    # lemmas true_k; production's lemma_fill_N (loop.py --climb-hints numbers the dirs' true.tsv rows per original,
    # differently at each refresh) is matched by formula through the goal's printed proof, loops/UL/proofs/<goal>:
    # that proof's axiom list is an alternative record of the goal (any proof from trusted premises will do).
    def norm(f):
        f = re.sub(r'^\s*!\s*\[[^\]]*\]\s*:\s*', '', f.strip().rstrip('.'))
        if '=' not in f or '!=' in f:
            return None
        ren = {}
        f = re.sub(r'\b[A-Z][A-Za-z0-9_]*\b', lambda m: ren.setdefault(m.group(0), f'V{len(ren)}'), f.replace(' ', ''))
        l, r = f.split('=', 1)
        ren2 = {}
        g2 = re.sub(r'\bV\d+\b', lambda m: ren2.setdefault(m.group(0), f'W{len(ren2)}'), r + '=' + l)
        return min(f, g2.replace('W', 'V'))
    frec = {}                                   # FILL node -> deps (None: unresolved)
    forms = collections.defaultdict(set)        # FORM node -> its FILL nodes
    norec = {}                                  # FILL node without a premise record -> its FORM node
    nfp = 0
    for p in glob.glob(os.path.join(L, '*', 'true.tsv')):
        d = p.split('/')[-2]
        prem = {}
        pp = os.path.join(L, d, 'fillprem.tsv')
        if os.path.exists(pp):
            for l in open(pp):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 6:
                    prem[(w[0], w[1])] = (w[3], [x for x in w[5].split(',') if x])
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) < 3:
                continue
            node = f'FILL:{d}:{w[0]}:{w[1]}'
            nf = norm(w[2])
            if nf:
                forms[f'FORM:{w[0]}:{nf}'].add(node)
            if (w[0], w[1]) not in prem and nf:
                norec.setdefault(node, f'FORM:{w[0]}:{nf}')
            if (w[0], w[1]) not in prem or node in frec:
                continue
            t, names = prem[(w[0], w[1])]
            deps = set()
            for x in names:
                if re.fullmatch(r'true_\d+', x):
                    deps.add(f'FILL:{d}:{w[0]}:{x}'); continue
                r = resolve(t, d, x)
                if r is None:
                    deps = None; break
                if r:
                    deps.add(r)
            frec[node] = deps; nfp += 1
    # (25 Nov 23:55) a fill lemma without a premise record in its dir (CLQ83's true.tsv began as a copy of CLS71's, whose
    # fillprem.tsv holds the records) rests on its formula: trusted when another fill lemma of the same original and
    # formula is (the fixpoint adds a node only once its deps are trusted, so a copy cannot vouch for itself).
    # CLQ83's listened nil3_23_32_to_27__goal_581 (an exposed original) used ten such copies
    for node, fm in norec.items():
        if node not in frec:
            frec[node] = {fm}
    # exp/fillcheck.py's re-proofs of old fill lemmas (no fillprem record): proved rows, premises from USEDAXIOMS
    pc = os.path.join(L, 'TRUSTNOW', 'fillcheck.tsv')
    for i, l in enumerate(open(pc) if os.path.exists(pc) else ()):
        w = l.rstrip('\n').split('\t')
        if len(w) < 6 or w[2] != '1':
            continue
        nf = norm(w[1])
        if not nf:
            continue
        node = f'FILL:fillcheck:{w[0]}:{i}'
        forms[f'FORM:{w[0]}:{nf}'].add(node)
        deps = set()
        for x in (x for x in w[3].split(',') if x):
            r = resolve(w[5], 'UL', x)
            if r is None:
                deps = None; break
            if r:
                deps.add(r)
        frec[node] = deps; nfp += 1
    # the climbers' real proofs that used true_k: the record is unresolved (resolve() gives None for 'true'), so
    # it is redone here with the dir's fill nodes, as an alternative record
    alt = {}                                    # goal -> [deps of another record]; trusted when one is
    for p in glob.glob(os.path.join(L, '*', 'used.tsv')):
        d = p.split('/')[-2]
        if not os.path.exists(os.path.join(L, d, 'fillprem.tsv')):
            continue
        own = {l.split('\t')[0] for l in open(os.path.join(L, d, 'solved.tsv')) if l.split('\t')[1:2] == ['1']}
        last = {}
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 3 and w[0] in own and w[0] in S and same(d, w[0]):
                last[w[0]] = w
        for g, w in last.items():
            deps = set()
            for x in (x for x in w[2].split(',') if x):
                if re.fullmatch(r'true_\d+', x):
                    deps.add(f'FILL:{d}:{orig(g)}:{x}'); continue
                r = resolve(g, d, x)
                if r is None:
                    deps = None; break
                if r:
                    deps.add(r)
            if deps is not None:
                alt.setdefault(g, []).append(deps)
    ex_ = set()
    if '--exposed' in sys.argv:
        ex_ = {l.strip() for l in open(sys.argv[sys.argv.index('--exposed') + 1]) if l.strip()}
    nalt = 0
    for g in S:
        if orig(g) not in ex_ or (g in rec and rec[g] is not None):
            continue
        pf = os.path.join(L, 'UL', 'proofs', g)
        if not os.path.exists(pf):
            continue
        deps = set()
        for m in re.finditer(r'^Axiom \d+ \(([^)]*)\): (.*)$', open(pf, errors='replace').read(), re.M):
            x, f = m.group(1), m.group(2)
            if re.fullmatch(r'lemma_fill_\d+', x):
                nf = norm(f)
                if not nf:
                    deps = None; break
                deps.add(f'FORM:{orig(g)}:{nf}'); continue
            r = resolve(g, 'UL', x)
            if r is None:
                deps = None; break
            if r:
                deps.add(r)
        if deps is not None:
            alt.setdefault(g, []).append(deps); nalt += 1
    print(f'fill lemmas: {sum(len(v) for v in forms.values())} in true.tsv files, {nfp} with a premise record; '
          f'{nalt} exposed goals with a printed proof as an alternative record', flush=True)
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
            if (deps is not None and g in rec and deps <= trusted) or any(a_ <= trusted for a_ in alt.get(g, ())):
                trusted.add(g); changed = True
        for n_, deps in frec.items():
            if n_ not in trusted and deps is not None and deps <= trusted:
                trusted.add(n_); changed = True
        for n_, fs in forms.items():
            if n_ not in trusted and fs & trusted:
                trusted.add(n_); changed = True
    nfill = sum(1 for n_ in frec if n_ in trusted)
    trusted &= S
    un = sorted(S - trusted)
    norec = sum(1 for g in un if g not in rec)
    unres = sum(1 for g in un if g in rec and rec[g] is None)
    open(out + '.untrusted', 'w').writelines(g + '\n' for g in un)
    if '--dump-rec' in sys.argv:
        # (21 Nov 00:50) every solved goal's record: its lemma goals, UNRES for an unresolved name, none without one
        # (exp/roots.py)
        with open(sys.argv[sys.argv.index('--dump-rec') + 1], 'w') as f:
            for g in sorted(S):
                r_ = rec.get(g, 0)
                f.write(f'{g}\t{"NOREC" if r_ == 0 else "UNRES" if r_ is None else ",".join(sorted(r_))}\n')
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
          f'{len(un) - norec - unres} using an untrusted or unsolved lemma); {nfill} fill lemmas trusted', flush=True)


if __name__ == '__main__':
    main()
