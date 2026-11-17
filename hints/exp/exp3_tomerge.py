#!/usr/bin/env python3
"""exp3/tomerge.py OUTDIRS... DIR: the proofs in run outputs (DIR/out-style files <goal>, from exp3/run.py or
exp4) as a loop dir for merge.py: DIR/solved.tsv (goal, round 1, CPU 0) and DIR/hints/<goal>, the proof's lemmas
and goal lines in the loop's canonical form (loop.py's canon_key over the problem's signature). The first output
dir with a proof of a goal wins. The runs' lemmas are production's proven goals, so the proofs are sound."""
import os, sys
sys.path.insert(0, '/project/twee/hints')
import hintlib
*src, dst = sys.argv[1:]
os.makedirs(f'{dst}/hints', exist_ok=True)
done = {l.split('\t')[0] for l in open(f'{dst}/solved.tsv')} if os.path.exists(f'{dst}/solved.tsv') else set()
with open(f'{dst}/solved.tsv', 'a') as f:
    for d in src:
        for g in sorted(os.listdir(d)):
            name = g[:-4] if g.endswith('.out') else g
            if name in done or '__goal_' not in name: continue
            out = open(os.path.join(d, g), errors='replace').read()
            if 'HINTS-END' not in out or 'RESULT: Theorem' not in out: continue
            L, G = hintlib.extract_hints(out); sig = hintlib.problem_signature(name)
            seen, hs = set(), []
            for l, r in L + G:
                if l == r: continue
                k = min(hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig))
                if k[0] != k[1] and k not in seen: seen.add(k); hs.append(k)
            open(f'{dst}/hints/{name}', 'w').write(''.join(f'{l}\t{r}\n' for l, r in hs))
            f.write(f'{name}\t1\t0\n'); done.add(name); print('proof', name, 'from', d, len(hs), 'hints')
