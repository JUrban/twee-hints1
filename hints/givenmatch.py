#!/usr/bin/env python3
"""(20 Nov) Unsolved goals that some successful run derived along the way (exp38, notes/2026-11-20-given-transfer.md).

transfer.py matches unsolved goals against the steps of proofs (hints files). Every successful run's given log
(loops/*/given/NAME: label, index, lhs, rhs, parents) also holds the rules it derived and did not use: about 380 M,
against 22 M proof steps. A rule derived in a run on an unconditional unit goal is a consequence of that original's
axioms and the run's (proven) lemmas. So an unsolved goal of an original with the same or more axioms that is a
variant of such a rule is a theorem, and the rule's ancestry in that log (its parents, closed) is a proof sketch for it.

Twee prints each logged rule with its variables numbered in order of occurrence (checked: 66,797 of 66,797), so a
variant is a dict lookup of the raw (lhs, rhs) pair, against both orientations of each goal.

  givenmatch.py INDEX OUT.tsv [-j 4] [--loops-exclude REGEX]
OUT: goal, source loop, source name, rule index, label (0 not in that proof, 1 a proof step), ancestry size.

  givenmatch.py sketch OUT.tsv SKDIR GOALS.tsv [--per 3]
writes each hit's ancestry (index order, the matched rule last) to SKDIR/<goal>/<loop>/<source name> as hints, and
GOALS.tsv for transfer.py run (goal, the sketch files, 0).
"""
import os, re, sys
from multiprocessing import get_context

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, hintsel, lemmas

LOOPS = '/project/hintwork/loops'
ALL = '/project/hintwork/sets/all'
# (climbers' runs may use unproven assumptions; 'bad' loops are known broken)
EXCL = r'^(CL|FUD|SMK)|bad'

W = None   # (in the workers: key -> goals)


def gkeys(n):
    lits = hintsel.goal_lits(n)
    if len(lits) != 1 or not lits[0][0]:
        return None
    l, r = lits[0][1], lits[0][2]
    sig = set(re.findall(r'[a-z]\w*', l + ' ' + r))
    return {hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig)}


def ancestry(lines, idx):
    """indexes of the rule IDX and all its ancestors in a parsed log"""
    par = {}
    for w in lines:
        par[w[1]] = [p for p in w[4:6] if p != '0']
    out = set(); todo = [idx]
    while todo:
        x = todo.pop()
        if x in out:
            continue
        out.add(x); todo.extend(par.get(x, ()))
    return out


def scan(job):
    loop, name = job
    p = os.path.join(LOOPS, loop, 'given', name)
    hits = []
    try:
        f = open(p)
    except OSError:
        return hits
    with f:
        for l in f:
            w = l.split('\t', 4)   # (label, index, lhs, rhs, the rest: the whole log is parsed only on a hit)
            if len(w) >= 4 and w[0] != '-1':
                gs = W.get((w[2], w[3].rstrip('\n')))
                if gs:
                    hits.extend((g, w[1], w[0]) for g in gs)
    if hits:
        lines = [l.rstrip('\n').split('\t') for l in open(p)]
        hits = [(g, loop, name, i, lab, len(ancestry(lines, i))) for g, i, lab in hits]
    return hits


def init(w):
    global W
    W = w


def sketch(hits, skdir, goals, per=3):
    by = {}
    for l in open(hits):
        w = l.rstrip('\n').split('\t')
        by.setdefault(w[0], []).append(w)
    with open(goals, 'w') as fo:
        for g, hs in sorted(by.items()):
            fs = []
            for w in hs[:per]:
                _, loop, name, ridx = w[:4]
                lines = [x.rstrip('\n').split('\t') for x in open(os.path.join(LOOPS, loop, 'given', name))]
                keep = ancestry(lines, ridx)
                rows = [x for x in lines if len(x) >= 4 and x[1] in keep and x[0] != '-1']   # (axioms are axioms)
                rows.sort(key=lambda x: int(x[1]))
                p = os.path.abspath(os.path.join(skdir, g, loop, name))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, 'w') as f:
                    f.writelines(f'{x[2]}\t{x[3]}\n' for x in rows)
                fs.append(p)
            fo.write(f'{g}\t{",".join(fs)}\t0\n')
    print(f'{len(by)} goals -> {goals}')


def main():
    if sys.argv[1] == 'sketch':
        per = int(sys.argv[sys.argv.index('--per') + 1]) if '--per' in sys.argv else 3
        return sketch(sys.argv[2], sys.argv[3], sys.argv[4], per)
    idx, out = sys.argv[1], sys.argv[2]
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 4
    excl = sys.argv[sys.argv.index('--loops-exclude') + 1] if '--loops-exclude' in sys.argv else EXCL
    S = {l.split('\t')[0] for l in open(os.path.join(LOOPS, 'UL', 'solved.tsv'))}
    want = {}
    ng = 0
    for n in (l.strip() for l in open(ALL)):
        if not n or n in S:
            continue
        try:
            ks = gkeys(n)
        except Exception:
            continue
        if ks:
            ng += 1
            for k in ks:
                want.setdefault(k, []).append(n)
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    tax = [axs(g) for gs in want.values() for g in gs]
    unit = {}; ucache = {}
    jobs = []
    for l in open(idx):
        w = l.rstrip('\n').split('\t')
        name, loop = w[0], w[1]
        if re.search(excl, loop):
            continue
        o = lemmas.split(name)[0]
        if o not in unit:
            try:
                unit[o] = None
                A = axs(name)
                # (a source original whose axioms are within no target's: nothing to give)
                unit[o] = any(A <= t for t in tax)
            except Exception:
                unit[o] = False
        if not unit[o]:
            continue
        if name not in ucache:
            try:
                ucache[name] = bool(lemmas.unit_eq(lemmas.conjecture(name) or '~'))
            except OSError:
                ucache[name] = False
        if ucache[name]:
            jobs.append((loop, name))
    print(f'{ng} unsolved unit goals, {len(jobs)} logs to scan ({j} workers)', flush=True)
    hits = {}
    with get_context('fork').Pool(j, initializer=init, initargs=(want,)) as pool:
        for k, hs in enumerate(pool.imap_unordered(scan, jobs, chunksize=64)):
            for h in hs:
                g, loop, name = h[0], h[1], h[2]
                if axs(name) <= axs(g):
                    hits.setdefault(g, []).append(h)
            if k % 50000 == 0:
                print(f'  {k} logs, {len(hits)} goals hit', flush=True)
    with open(out, 'w') as fo:
        for g in sorted(hits):
            # (smallest ancestry first: the shortest sketch)
            for h in sorted(set(hits[g]), key=lambda h: (h[5], h[1], h[2]))[:5]:
                fo.write('\t'.join(map(str, h)) + '\n')
    print(f'{len(hits)} unsolved goals are variants of rules derived in runs from the same or weaker axioms -> {out}')


if __name__ == '__main__':
    main()
