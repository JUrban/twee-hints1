#!/bin/bash
# Sketch climbing, first test (14 Nov 22:50; user's lattice-of-assumptions idea): sets/sg1 (32 gap-1 goals that
# failed L1), assumptions = 8 nearest unproven siblings by proof line (either side), up to 6 sketch runs of 5 s
# (doubling while the top set fails), then a real 20 s run with all sketch hints. Compare: S20 (fresh 20 s, no
# sketches), SD (fresh 80 s), SO (fresh 80 s, ordering 1), SG1 (resume +240 s).
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/sg1 loops/CL1 --m 8 --runs 6 --sketch-time 5 --final-time 20 -j 2 -- \
  --init loops/ULsJ --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e22 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CL1.log 2>&1
echo "CL1 $(tail -1 loops/CL1.log) $(date +%T)" | tee loops/CL1.done
