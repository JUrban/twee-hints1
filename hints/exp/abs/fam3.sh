#!/bin/bash
# Family test: the full up-down climb with one-axiom up steps (15 Nov 21:55; user: "the up step could also be
# adding another axiom"). As abs/fam2.sh's FUD (snapshot ULsX, goals in order, 1 worker, --chain) plus X.
#   SET=fam24 ARM=FUDs X="--up-single --up-levels 2 --up-beam 2 --up-width 4"
cd /project/hintwork
L="--init loops/ULsX --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
C="--m 8 --knn 8 --theories 4 --theory-lemmas 10 --updown --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 20"
python3 /project/twee/hints/climb.py sets/$SET loops/$ARM $C $X -j 1 -- $L --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(tail -1 loops/$ARM.log) $(date +%T)" | tee loops/$ARM.done
