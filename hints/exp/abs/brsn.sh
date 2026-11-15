#!/bin/bash
# Resume without re-scoring the saved queue (14 Nov 16:20): the requeue costs 20-55 s per resume of a 20 s state
# (RSa: ~20 us per passive, 1-2M passives), 50-100% of a 20 s round, ~15-25% of the cascade's 80 s level.
# BRSn = BRS (abs/bl.sh) + --no-resume-requeue. Starts with the bl.sh arms, after the lemma-usage probe (LUSE).
while ps -eo args | grep -q "[l]oop.py sets/u3n73\|[l]oop.py sets/r4s60"; do sleep 60; done
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/fr100 loops/BRSn --init loops/ULsI --start 1 --timeout 20 --twee /project/bin/twee-e30 \
  --keep-out -j 2 --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --rounds 4 --resume \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue" > loops/BRSn.log 2>&1
echo "BRSn $(awk -F'\t' '$2>0' loops/BRSn/solved.tsv | wc -l) $(date +%T)" | tee loops/BRSn.done
