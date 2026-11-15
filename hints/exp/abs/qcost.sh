#!/bin/bash
# Queue renormalisation charge test (REPORT 2v): every other goal of sets/v2_hard (34), 120 abstract s,
# twee-e27, rm4t + 6 lemmas either side + 10 subset kNN, whole-original pools; --queue-cost 0 vs 0.008.
until [ -s /project/hintwork/loops/N3x6.done ]; do sleep 60; done
cd /project/hintwork
V="python3 /project/twee/hints/loop.py sets/v2_half"
C="--init loops/V2base --start 1 --rounds 1 --timeout 120 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-after --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e27 --keep-out -j 5 --pool original --wall-factor 15"
for q in 0 0.008; do
  n=V2q${q/0./}
  $V loops/$n $C --args="--abstract-time 2000 --max-cpu 1200 --queue-cost $q --progress 20" > loops/$n.log 2>&1
  echo "$n $(grep -c THM loops/$n/r1/results.tsv) $(date +%T)" | tee loops/$n.done
done
