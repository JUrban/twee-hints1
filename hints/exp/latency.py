#!/usr/bin/env python3
"""(21 Nov 00:48) How long a from-zero loop takes to use a lemma once it has it (notes/2026-11-21-roots.md).

For each goal DIR's own loop proved (its first THM row in DIR/r*/results.tsv, time t=) with a kept output naming
lemma goals (USEDAXIOMS: lemma_goal_J, lemma_knn_I_<goal>): the time its last lemma became available (the lemma's
hints file mtime against DIR's start, config.json's mtime; this covers the side writers' proofs too), the delay to
the goal's proof, and how many runs of the goal came between (failed ones: runs after its last lemma that still
failed, from a different context or a too short limit).

  latency.py DIR [--start EPOCH]
"""
import collections, glob, os, re, statistics, sys


def main():
    a = sys.argv[1:]
    d = a[0]
    t0 = float(a[a.index('--start') + 1]) if '--start' in a else os.path.getmtime(os.path.join(d, 'config.json'))
    first, runs = {}, collections.defaultdict(list)
    for p in sorted(glob.glob(f'{d}/r*/results.tsv')):
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            m = re.search(r'\bt=(\d+)', l)
            if len(w) < 5 or not m:
                continue
            t = int(m.group(1))
            runs[w[0]].append((t, w[1] == 'THM', w[4]))
            if w[1] == 'THM' and w[0] not in first:
                first[w[0]] = (t, w[4], p)
    T = {}
    hd = os.path.join(d, 'hints')
    for g in os.listdir(hd):
        try:
            T[g] = os.path.getmtime(os.path.join(hd, g)) - t0
        except OSError:
            pass
    orig = lambda g: g.rsplit('__goal_', 1)[0]
    rows = []
    nodep = nout = 0
    LK = collections.defaultdict(collections.Counter)
    for g, (t, lab, p) in first.items():
        op = os.path.join(os.path.dirname(p), 'out', g)
        try:
            m = re.search(r'^USEDAXIOMS (.*)$', open(op, errors='replace').read(), re.M)
        except OSError:
            nout += 1; continue
        if not m:
            nout += 1; continue
        deps, kind = set(), {}
        for x in m.group(1).split():
            mm = re.match(r'(?:lemma|assume)_goal_(\d+)$', x)
            if mm:
                y = f'{orig(g)}__goal_{mm.group(1)}'; deps.add(y)
                kind[y] = ('sib', int(g.rsplit('_', 1)[1]) - int(mm.group(1)))
            mm = re.match(r'(?:lemma|assume)_knn_(\d+)_(.+__goal_\d+)$', x)
            if mm:
                deps.add(mm.group(2)); kind.setdefault(mm.group(2), ('knn', int(mm.group(1))))
        deps = {x for x in deps if x in T}
        if not deps:
            nodep += 1; continue
        last = max(T[x] for x in deps)
        lk = kind[max(deps, key=lambda x: T[x])]
        LK[(lk[0], (min(lk[1], 4) if lk[0] == 'sib' and lk[1] > 0 else 'before' if lk[0] == 'sib' else
                    min(lk[1] // 5 * 5, 25)))][int(last // 3600 >= 1), int(t - last > 600)] += 1
        between = sum(1 for (tt, ok, _) in runs[g] if last <= tt < t and not ok)
        before = sum(1 for (tt, ok, _) in runs[g] if tt < last)
        rows.append((g, t, lab, last, t - last, between, before, len(deps)))
    print(f'{d}: {len(first)} goals proved by the loop; {len(rows)} with lemmas, {nodep} with none, {nout} without '
          f'a kept output')
    W = 3600
    by = collections.defaultdict(list)
    for r in rows:
        by[int(r[3] // W)].append(r)
    print('last lemma in hour | goals | delay median, p75, p90 (min) | runs after it that failed: 0, 1, 2+ | '
          'runs before it')
    for h in sorted(by):
        rs = by[h]
        ds = sorted(r[4] / 60 for r in rs)
        q = lambda f: ds[min(len(ds) - 1, int(f * len(ds)))]
        b = collections.Counter(min(r[5], 2) for r in rs)
        print(f'  {h:>2} | {len(rs):>6} | {statistics.median(ds):6.1f} {q(.75):6.1f} {q(.9):6.1f} | '
              f'{b[0]:>5} {b[1]:>5} {b[2]:>5} | {sum(r[6] for r in rs) / len(rs):.1f}')
    print('the last lemma: kind, sibling distance (goal numbers; 4 = 4 or more) or kNN rank (by 5s) | after hour 1: '
          'delay <= 10 min, > 10 min | in hour 0: <= 10, > 10')
    for k in sorted(LK, key=str):
        c = LK[k]
        print(f'  {k[0]} {k[1]!s:>6} | {c[1, 0]:>6} {c[1, 1]:>6} | {c[0, 0]:>6} {c[0, 1]:>6}')
    lab = collections.Counter(r[2] for r in rows if r[4] > 1800)
    print('delayed over 30 min, by proving label: ' + ', '.join(f'{k} {v}' for k, v in lab.most_common(8)))


if __name__ == '__main__':
    main()
