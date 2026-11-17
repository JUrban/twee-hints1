#!/usr/bin/env python3
"""Check that a loop's proofs do not depend on each other in a circle (17 Nov, the user's question).

A run gets as lemma axioms only goals proven before it (sibling goals lemma_goal_<j> of the same original,
kNN goals lemma_knn_<i>_<goal>), and a solved goal is not run again, so along solved.tsv every proof should
use only goals proven earlier: then each goal has a proof from its axioms (inline the lemmas' proofs
recursively, which ends because each step goes back in time). This checks it on the proofs whose output the
loop kept (--keep-out: DIR/r*/out/<goal>, twee's USEDAXIOMS line, printed since twee-e31, 14 Nov 16:13):

* every lemma a proof used is a goal whose first row in DIR/solved.tsv comes before the proof's own row. A
  goal can have several rows: a side worker's proof (the live transfer, time 0) is synced every 60 s, so the
  loop can run and prove the goal again in between, and that later run's output is the kept one; its row
  is the goal's last row. (The first proof then is the side worker's, which keeps no output; its lemmas
  come from its copy of the loop's proven goals, so they are earlier ones.)
* the graph goal -> lemma goals of the recorded proofs has no cycle;
* how many proofs use no lemma (standalone), and the depth of lemma chains among the recorded proofs;
* that each used lemma is a theorem of the target's theory: the source goal's axioms (its own problem file,
  not the original's first file as lemmas.axiom_set reads them) are a subset of the target's, as clause bodies
  with whitespace dropped (a renamed variant would show up here as a false alarm).

Lemma names without their source goal (lemma_knn_<i>, before 14 Nov 16:13; lemma_<i> of --multi runs) are
counted as unmapped.

usage: depcheck.py DIR [--list N]   (prints the first N violations)
"""
import sys, os, re, glob, subprocess, collections


def used_lemmas(d):
    """goal -> (set of source goals, unmapped names) from the kept outputs' USEDAXIOMS lines."""
    outs = sorted(glob.glob(os.path.join(d, 'r*', 'out')))
    res = {}
    for od in outs:
        p = subprocess.run(['grep', '-r', '-m1', '^USEDAXIOMS', od], capture_output=True, text=True)
        for line in p.stdout.splitlines():
            path, _, rest = line.partition(':USEDAXIOMS')
            g = os.path.basename(path)
            o = g.rsplit('__goal_', 1)[0]
            src, unm = set(), []
            for x in rest.split():
                m = re.match(r'lemma_knn_\d+_(\S+__goal_\d+)$', x)
                if m:
                    src.add(m.group(1)); continue
                m = re.match(r'lemma_goal_(\d+)$', x)
                if m:
                    src.add(f'{o}__goal_{m.group(1)}'); continue
                if x.startswith(('lemma_', 'cut_', 'true_', 'assume_', 'src_')):
                    unm.append(x)
            res[g] = (src, unm)
    return res


AIM_PROB = os.environ.get('AIM_PROB', '/project/AIM60k/problems/tptp')
_ax = {}
def axioms(g):
    if g not in _ax:
        out = set()
        for l in open(os.path.join(AIM_PROB, g + '.p')):
            if l.startswith(('cnf(', 'fof(')) and 'conjecture' not in l:
                out.add(re.sub(r'\s+', '', l.split(',', 2)[2].rsplit(')', 1)[0]))
        _ax[g] = frozenset(out)
    return _ax[g]


def main():
    a = sys.argv[1:]
    nlist = 10
    if '--list' in a:
        i = a.index('--list'); nlist = int(a[i + 1]); del a[i:i + 2]
    d = a[0]
    pos, last = {}, {}
    for i, l in enumerate(open(os.path.join(d, 'solved.tsv'))):
        g = l.split('\t', 1)[0].strip()
        if g:
            pos.setdefault(g, i); last[g] = i
    U = {g: v for g, v in used_lemmas(d).items() if g in pos}
    viol, unsolved_src, unm = [], [], 0
    for g, (src, un) in U.items():
        unm += bool(un)
        for s in src:
            if s not in pos:
                unsolved_src.append((g, s))
            elif pos[s] >= last[g]:
                viol.append((g, s, last[g], pos[s]))
    # the lemma's theory is the target's or weaker
    badax, nax = [], 0
    for g, (src, _) in U.items():
        for s_ in src:
            nax += 1
            try:
                if not axioms(s_) <= axioms(g):
                    badax.append((g, s_, len(axioms(s_) - axioms(g))))
            except FileNotFoundError as e:
                badax.append((g, s_, 'no file'))
    # cycles among the recorded proofs (iterative DFS)
    state, cyc = {}, []
    for g0 in U:
        if g0 in state:
            continue
        stack = [(g0, iter(sorted(U[g0][0])))]; state[g0] = 1
        while stack:
            g, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[g] = 2; stack.pop(); continue
            if nxt not in U:
                continue
            if state.get(nxt) == 1:
                cyc.append([x for x, _ in stack] + [nxt])
            elif nxt not in state:
                state[nxt] = 1; stack.append((nxt, iter(sorted(U[nxt][0]))))
    # depth of lemma chains (0 = no lemma used) among the recorded proofs, by solved order
    depth = {}
    for g in sorted(U, key=lambda x: pos[x]):
        depth[g] = 1 + max((depth.get(s, 0) for s in U[g][0]), default=-1) if U[g][0] else 0
    n = len(U)
    print(f'{d}: {len(pos)} solved goals, {n} with a kept output naming the axioms it used')
    print(f'  goals with several rows (proved again before a side worker\'s row was synced): '
          f'{sum(1 for g in pos if last[g] != pos[g])}')
    print(f'  proofs using no lemma: {sum(1 for v in U.values() if not v[0] and not v[1])} '
          f'({100 * sum(1 for v in U.values() if not v[0] and not v[1]) / max(1, n):.1f}%)')
    print(f'  proofs using lemmas without a source name (old naming): {unm}')
    nl = collections.Counter(len(v[0]) for v in U.values())
    print('  lemma goals used per proof: ' + ', '.join(f'{k}: {nl[k]}' for k in sorted(nl)))
    dc = collections.Counter(depth.values())
    print('  lemma-chain depth within the recorded proofs: ' + ', '.join(f'{k}: {dc[k]}' for k in sorted(dc)))
    print(f'  used lemma proven LATER than the proof (or the same row): {len(viol)}')
    for v in viol[:nlist]:
        print('    %s uses %s (rows %d, %d)' % v)
    print(f'  used lemma not in solved.tsv: {len(unsolved_src)}')
    for v in unsolved_src[:nlist]:
        print('    %s uses %s' % v)
    print(f'  used lemmas whose axioms are not a subset of the target\'s: {len(badax)} of {nax}')
    for v in badax[:nlist]:
        print('    %s uses %s (%s axioms not in the target)' % v)
    print(f'  cycles among the recorded proofs: {len(cyc)}')
    for c in cyc[:nlist]:
        print('    ' + ' -> '.join(c))


if __name__ == '__main__':
    main()
