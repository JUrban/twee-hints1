#!/bin/bash
# Family test, second set and ablation (15 Nov 21:15). As abs/fam.sh (snapshot ULsX, goals in order, 1 worker, --chain).
#   SET=fam1243b2 ARM=FUD2: the full up-down climb; ARM=F80b: fresh 80 s control
#   SET=fam24 ARM=FUDnt: the full climb without stronger theories (--theories 0)
cd /project/hintwork
L="--init loops/ULsX --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
case $ARM in
  F80*) C="--m 0 --knn 0 --updown --chain --final-time 80";;
  FUDnt) C="--m 8 --knn 8 --theories 0 --updown --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 16 --sketch-time 5 --final-time 20";;
  *) C="--m 8 --knn 8 --theories 4 --theory-lemmas 10 --updown --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 16 --sketch-time 5 --final-time 20";;
esac
python3 /project/twee/hints/climb.py sets/$SET loops/$ARM $C -j 1 -- $L --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(tail -1 loops/$ARM.log) $(date +%T)" | tee loops/$ARM.done
