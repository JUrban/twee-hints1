#!/bin/bash
# (22 Nov 11:10) smoke for exp57 (twee's critical-pair weights as members): 3 late2 goals, 5 s, control and --lhs-weight 2
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
run() { D=$1; X=$2
python3 -u /project/twee/hints/loop.py sets/wsm3 loops/$D --init loops/LAA.ctx --start 1 --rounds 1 --keep-out -j 1 \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout 5 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider $X" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv) $(date +%T)" | tee loops/$D.done; }
run WSM0 "" &
run WSM1 "--lhs-weight 2" &
wait
