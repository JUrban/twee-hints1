#!/bin/bash
# ho3u battery in abstract time (16000 CPs = 8 abstract s)
cd /project/hintwork
R="python3 /project/twee/hints/run.py sets/ho3_unsolved"
B="--twee /project/bin/twee-e15 --timeout 8 --wall-factor 5 -j 6"
A="--abstract-time 2000"
M4="--rule-model /project/hintwork/models/rm4.bin --rule-vocab /project/hintwork/models/rm4.vocab --rule-threshold 0.1 --rule-penalty 2"
MT="--rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-threshold 0.1 --rule-penalty 2"
$R runs/a_ho3u_plain $B --args="$A" > abs/a_ho3u_plain.log 2>&1 &
$R runs/a_ho3u_rm4 $B --args="$A $M4" --per rule-goal:goals/rm4_ho3 > abs/a_ho3u_rm4.log 2>&1 &
$R runs/a_ho3u_rm4t $B --args="$A $MT" --per rule-goal:goals/rm4t_ho3 > abs/a_ho3u_rm4t.log 2>&1 &
wait
$R runs/a_ho3u_rm4_lem3 $B --prob-dir probs/ho3u_lem3 --args="$A $M4" --per rule-goal:goals/rm4_ho3 > abs/a_ho3u_rm4_lem3.log 2>&1 &
$R runs/a_ho3u_rm4_lem6 $B --prob-dir probs/ho3u_lem6 --args="$A $M4" --per rule-goal:goals/rm4_ho3 > abs/a_ho3u_rm4_lem6.log 2>&1 &
$R runs/a_ho3u_rm4t_lem3 $B --prob-dir probs/ho3u_lem3 --args="$A $MT" --per rule-goal:goals/rm4t_ho3 > abs/a_ho3u_rm4t_lem3.log 2>&1 &
wait
for d in plain rm4 rm4t rm4_lem3 rm4_lem6 rm4t_lem3; do echo "$d $(grep -c THM runs/a_ho3u_$d/results.tsv)"; done
