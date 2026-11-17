#!/usr/bin/env python3
"""exp1 goal selection, as run on 17 Nov 18:59 from /project/hintwork: 200 of the UL proofs whose kept output
records lemmas that all map to goals (then 2,749), seed 1 -> exp1/s200 (= exp/sets/exp1_s200). Deterministic
given loops/UL's state at that time; UL has grown since, so the committed set is the record."""
import sys, random
sys.path.insert(0, '/project/twee/hints')
from depcheck import used_lemmas
r = used_lemmas('loops/UL')
g = sorted(x for x, (s, u) in r.items() if s and not u)
print(len(r), 'recorded', len(g), 'with mapped lemmas')
random.seed(1); s = sorted(random.sample(g, 200))
open('exp1/s200', 'w').write(''.join(x + '\n' for x in s))
