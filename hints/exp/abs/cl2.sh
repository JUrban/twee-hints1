#!/bin/bash
# Sketch climbing on sets/sg1 (32 stalled goals), 14 Nov 23:00: candidates = 8 nearest unproven siblings + Veroff-style
# laws (commutativity/associativity, defined ops trivial; collapsing laws dropped) + 8 frequent equations.
# Up to 12 sketch runs of 5 s (doubling up to 20 s while the top set fails; ban-and-restart when stuck), then a
# real 20 s run with all sketch hints. CL3 adds --fill 3: after each sketch proof one 3 s multi-goal run tries to
# prove the proof's assumption-dependent lemmas without assumptions; proven ones become axioms (true lemmas).
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/sg1 loops/CL2 --m 8 --laws --freq 8 --runs 12 --sketch-time 5 --final-time 20  -j 2 -- \
  --init loops/ULsJ --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e37 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CL2.log 2>&1
echo "CL2 $(tail -1 loops/CL2.log) $(date +%T)" | tee loops/CL2.done
