import sys, re
sys.path.insert(0, '/project/twee/hints'); import depcheck
for d in sys.argv[1:]:
    U = depcheck.used_lemmas(d)
    n = len(U); ab = be = kn = 0
    for g, (src, _) in U.items():
        o, k = g.rsplit('__goal_', 1); k = int(k)
        sib = [int(s.rsplit('__goal_', 1)[1]) for s in src if s.rsplit('__goal_', 1)[0] == o]
        ab += any(j > k for j in sib); be += any(j < k for j in sib); kn += any(s.rsplit('__goal_', 1)[0] != o for s in src)
    print(f'{d}: {n} recorded proofs; use a later sibling {ab} ({100*ab/n:.1f}%), an earlier sibling {be} ({100*be/n:.1f}%), a goal of another original {kn} ({100*kn/n:.1f}%)')
