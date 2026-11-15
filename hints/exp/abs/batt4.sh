#!/bin/bash
cd /project/hintwork
until [ -s /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/bvbtoqz8e.output ]; do sleep 10; done
R="python3 /project/twee/hints/run.py sets/r1sim"
B="--twee /project/bin/twee-e15 --timeout 4 --wall-factor 5 -j 6"
A="--abstract-time 2000"
M4="--rule-model /project/hintwork/models/rm4.bin --rule-vocab /project/hintwork/models/rm4.vocab --rule-threshold 0.1 --rule-penalty 2"
MT="--rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-threshold 0.1 --rule-penalty 2"
$R runs/a_r1_rm4 $B --args="$A $M4" --per rule-goal:goals/rm4_r1sim > abs/a_r1_rm4.log 2>&1 &
for v in lem3 lem3k3s; do
  $R runs/a_r1_rm4_$v $B --prob-dir probs/r1sim_$v --args="$A $M4" --per rule-goal:goals/rm4_r1sim > abs/a_r1_rm4_$v.log 2>&1 &
done
wait
for v in k6s lem3k10s; do
  $R runs/a_r1_rm4_$v $B --prob-dir probs/r1sim_$v --args="$A $M4" --per rule-goal:goals/rm4_r1sim > abs/a_r1_rm4_$v.log 2>&1 &
done
$R runs/a_r1_rm4t $B --args="$A $MT" --per rule-goal:goals/rm4t_r1sim > abs/a_r1_rm4t.log 2>&1 &
wait
for d in rm4 rm4_lem3 rm4_lem3k3s rm4_k6s rm4_lem3k10s rm4t; do echo "$d $(grep -c THM runs/a_r1_$d/results.tsv)"; done
