#!/bin/bash
# Sketch climbing with true assumptions only (14 Nov 23:40): 8 nearest unproven siblings + 8 kNN unproven goals of other
# originals (axioms a subset of the target's), gap filling --fill 3 (every dependent lemma is true). sets/sg3, as CL3.
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/sg3 loops/CL5 --m 8 --knn 8 --runs 12 --sketch-time 5 --final-time 20 --fill 3 -j 2 -- \
  --init loops/ULsK --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e37 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CL5.log 2>&1
echo "CL5 $(tail -1 loops/CL5.log) $(date +%T)" | tee loops/CL5.done
