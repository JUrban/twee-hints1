#!/bin/bash
# Learned lattice moves (15 Nov 23:10; user: learn the up/down steps, randomized guidance). FUD2's config (abs/fam2.sh)
# on sets/fam1243b2 (not in the policy's training rows) plus X, e.g.
#   SET=fam1243b2 ARM=FUD2p X="--move-model /project/hintwork/models/lattice1.json --move-temp 1 --move-eps 0.1"
cd /project/hintwork
L="--init loops/ULsX --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
C="--m 8 --knn 8 --theories 4 --theory-lemmas 10 --updown --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 16 --sketch-time 5 --final-time 20"
python3 /project/twee/hints/climb.py sets/$SET loops/$ARM $C $X -j 1 -- $L --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(tail -1 loops/$ARM.log) $(date +%T)" | tee loops/$ARM.done
