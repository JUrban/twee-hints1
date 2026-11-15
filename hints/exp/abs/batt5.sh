#!/bin/bash
cd /project/hintwork
until [ -s /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/be7bfsebo.output ]; do sleep 10; done
R="python3 /project/twee/hints/run.py sets/r1sim"
B="--twee /project/bin/twee-e15 --timeout 4 --wall-factor 5 -j 9"
M4="--rule-model /project/hintwork/models/rm4.bin --rule-vocab /project/hintwork/models/rm4.vocab --rule-threshold 0.1 --rule-penalty 2"
for r in 1990 2010; do
  $R runs/a_r1_rm4_at$r $B --args="--abstract-time $r $M4" --per rule-goal:goals/rm4_r1sim > abs/a_r1_rm4_at$r.log 2>&1 &
done
wait
for r in 1990 2010; do echo "rm4_at$r $(grep -c THM runs/a_r1_rm4_at$r/results.tsv)"; done
