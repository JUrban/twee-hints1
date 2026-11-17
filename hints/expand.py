#!/usr/bin/env python3
"""Expand lemma-based proofs back to the axioms, Veroff style (17 Nov, the user's suggestion).

A loop proof of G often uses proven goals as lemma axioms (siblings lemma_goal_<j>, kNN goals
lemma_knn_<i>_<goal>). Its hint file then holds only the steps after the lemmas. The expansion of G is G's
steps plus, recursively, the steps of every lemma it used (each lemma's own hint file holds its proof's steps
and its statement). As hints these let a run from the axioms alone rebuild the lemmas on the way.

Which lemmas a proof used comes from the kept outputs' USEDAXIOMS lines (depcheck.used_lemmas), read from
the LOOPS in order: the first loop with a record of a goal gives its lemmas and its hint file. A goal without
a record anywhere enters as a leaf (its hint file from the first loop that has one) and makes the expansion
incomplete. Records with lemma names that map to no goal (assumed or cut conjectures) are skipped, so a
sketch's steps never enter. Mixing loops can make the graph cyclic; the closure is a set, so that is
harmless for hints. Only a rerun from the axioms shows that the steps suffice.

usage: expand.py NAMES OUTDIR [--loops L1,L2,...] [--base /project/hintwork/loops] [--max N]
  writes OUTDIR/<goal> (lhs<TAB>rhs, own steps first, then by depth, duplicates dropped, at most N lines)
  and OUTDIR.tsv: goal, closure size, depth, unrecorded members, hints, own hints, recorded loop.
"""
import argparse, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depcheck import used_lemmas

LOOPS = 'UL,Z4,Z3,Z2,Z1,Z0,PGA,PGB,ORH,ORG,ORF,ORE,ORD,ORC,ORB,ORA'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names'); ap.add_argument('outdir')
    ap.add_argument('--loops', default=LOOPS); ap.add_argument('--base', default='/project/hintwork/loops')
    ap.add_argument('--max', type=int, default=100000)
    a = ap.parse_args()
    loops = [os.path.join(a.base, x) for x in a.loops.split(',')]
    rec = {}   # goal -> (loop dir, source goals)
    for d in loops:
        if not os.path.isdir(d):
            continue
        for g, (src, unm) in used_lemmas(d).items():
            if g not in rec and not unm and os.path.exists(os.path.join(d, 'hints', g)):
                rec[g] = (d, src)
    print(f'{len(rec)} recorded proofs from {len(loops)} loops', file=sys.stderr)

    def hint_file(g):
        if g in rec:
            return os.path.join(rec[g][0], 'hints', g)
        for d in loops:
            p = os.path.join(d, 'hints', g)
            if os.path.exists(p):
                return p
        return None

    os.makedirs(a.outdir, exist_ok=True)
    names = [l.strip() for l in open(a.names) if l.strip()]
    with open(a.outdir.rstrip('/') + '.tsv', 'w') as st:
        for g in names:
            depth = {g: 0}; order = [g]; q = collections.deque([g]); unrec = 0
            while q:
                x = q.popleft()
                if x not in rec:
                    unrec += x != g
                    continue
                for y in sorted(rec[x][1]):
                    if y not in depth:
                        depth[y] = depth[x] + 1; order.append(y); q.append(y)
            seen, out, own = set(), [], 0
            for x in order:
                p = hint_file(x)
                if p is None:
                    continue
                for l in open(p):
                    w = l.rstrip('\n').split('\t')
                    if len(w) < 2:
                        continue
                    k = (w[0], w[1]) if w[0] <= w[1] else (w[1], w[0])
                    if k in seen:
                        continue
                    seen.add(k); out.append(f'{w[0]}\t{w[1]}\n'); own += x == g
            with open(os.path.join(a.outdir, g), 'w') as f:
                f.writelines(out[:a.max])
            st.write(f'{g}\t{len(order)}\t{max(depth.values())}\t{unrec}\t{len(out)}\t{own}\t'
                     f'{os.path.basename(rec[g][0]) if g in rec else "-"}\n')


if __name__ == '__main__':
    main()
