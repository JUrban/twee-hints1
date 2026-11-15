#!/bin/bash
# Twee settings on stalled goals, retest from a valid snapshot (15 Nov 12:19; the 06:05 portfolio negative came from
# ULsM, which held only round-0 context). sets/p9no_v: 36 goals Prover9's worker failed (unfolding: 3 of the first
# 10, control 0). Production context, fresh 20 s, from ULsV; V0 is the control.
cd /project/hintwork
run() { D=$1; X=$2
python3 -u /project/twee/hints/loop.py sets/p9no_v loops/$D --init loops/ULsV --start 1 --rounds 1 --keep-out -j 1 \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider $X" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/36 $(date +%T)" | tee loops/$D.done; }
run V0 "" &
run V1 "--no-flatten-goal" &
run V2 "--flatten-goal-lightly" &
run V3 "--flip-ordering" &
run V4 "--kbo-weight0" &
wait
