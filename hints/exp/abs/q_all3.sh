#!/bin/bash
true
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/ALL_lem --start 3 --rounds 1 --timeout 2,2,2,2 -j 18 \
  --twee /project/bin/twee-e16 --pool knn:30:100 --args="--abstract-time 2000" \
  --model --model-fixed /project/hintwork/models/rm4.bin,/project/hintwork/models/rm4.vocab \
  --model-args "--rule-threshold 0.1 --rule-penalty 2" --hints-extra hints/train_pool,hints/tr30_g1_pool \
  --lemmas 3 --lemma-knn 10 --lemma-subsets > loops/ALL_lem_r3.log 2>&1
tail -2 loops/ALL_lem_r3.log
