#!/bin/bash
# Family test of the up-down climb (15 Nov 20:20; user: stronger theories, climb up and down, learn from the climbs).
# sets/fam24: the first 12 unsolved goals (in proof order) of aK2_eq_aK3_1243b (66 stronger theories) and nsmr_to_aa1
# (3), snapshot loops/ULsX (UL at 20:15). Goals in order, 1 worker; --chain: each proof is a sibling lemma and hints
# for the later targets at once.
#   ARM=FUD: siblings + kNN goals + 4 theories (+ their lemmas) + up (theory unions, weaker goals) and down, fill 3 s
#   ARM=F80: control, the same climb without assumptions: one fresh 80 s run per goal (with --chain)
cd /project/hintwork
L="--init loops/ULsX --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
if [ "$ARM" = F80 ]; then
  C="--m 0 --knn 0 --updown --chain --final-time 80"
else
  C="--m 8 --knn 8 --theories 4 --theory-lemmas 10 --updown --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 16 --sketch-time 5 --final-time 20"
fi
python3 /project/twee/hints/climb.py sets/fam24 loops/$ARM $C -j 1 -- $L --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(tail -1 loops/$ARM.log) $(date +%T)" | tee loops/$ARM.done
