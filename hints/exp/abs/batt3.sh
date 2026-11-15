#!/bin/bash
cd /project/hintwork
until [ -s /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/bvbtoqz8e.output ]; do sleep 10; done
R="python3 /project/twee/hints/run.py sets/ho3_unsolved"
B="--twee /project/bin/twee-e15 --timeout 8 --wall-factor 5 -j 5"
A="--abstract-time 2000"
M4="--rule-model /project/hintwork/models/rm4.bin --rule-vocab /project/hintwork/models/rm4.vocab --rule-threshold 0.1 --rule-penalty 2"
for v in lem3k3s lem3k10s; do
  $R runs/a_ho3u_rm4_$v $B --prob-dir probs/ho3u_$v --args="$A $M4" --per rule-goal:goals/rm4_ho3 > abs/a_ho3u_rm4_$v.log 2>&1 &
done
for h in all sub; do
  $R runs/a_ho3u_rm4_lem3_knn$h $B --prob-dir probs/ho3u_lem3 --args="$A $M4" --per rule-goal:goals/rm4_ho3 --per hints-file:hints/ho3u_knn_$h > abs/a_ho3u_rm4_lem3_knn$h.log 2>&1 &
done
wait
for v in lem3k3s lem3k10s lem3_knnall lem3_knnsub; do echo "rm4_$v $(grep -c THM runs/a_ho3u_rm4_$v/results.tsv)"; done
