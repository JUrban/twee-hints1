#!/bin/bash
until [ -s /project/hintwork/loops/V2p_r2.done ]; do sleep 30; done
cd /project/hintwork
R="python3 /project/twee/hints/run.py sets/r1sim"
B="--twee /project/bin/twee-e16 --timeout 4 --wall-factor 5 -j 6"
A="--abstract-time 2000"
M4="--rule-model /project/hintwork/models/rm4.bin --rule-vocab /project/hintwork/models/rm4.vocab --rule-threshold 0.1 --rule-penalty 2"
MT="--rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-threshold 0.1 --rule-penalty 2"
for h in all sub; do
  $R runs/a_r1_rm4_lem3k10s_knn$h $B --prob-dir probs/r1sim_lem3k10s --args="$A $M4" --per rule-goal:goals/rm4_r1sim --per hints-file:hints/r1sim_knn_$h > abs/a_r1_rm4_lem3k10s_knn$h.log 2>&1 &
done
$R runs/a_r1_rm4t_lem3k10s $B --prob-dir probs/r1sim_lem3k10s --args="$A $MT" --per rule-goal:goals/rm4t_r1sim > abs/a_r1_rm4t_lem3k10s.log 2>&1 &
wait
for d in rm4_lem3k10s_knnall rm4_lem3k10s_knnsub rm4t_lem3k10s; do echo "$d $(grep -c THM runs/a_r1_$d/results.tsv)"; done
