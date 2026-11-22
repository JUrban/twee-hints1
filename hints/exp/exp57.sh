#!/bin/bash
# exp57 (22 Nov 11:12, notes/2026-11-22-cp-weights.md; the user, 11:08: "have we played with different weights for the
# default twee weighting functions?"): twee's critical-pair weights as portfolio members. sets/wheads300: 300 random
# heads of sets/late2 (a late2 goal whose previous goal is proven in Z7's context), seed 57. Context loops/LAA.ctx
# (Z7's proofs without late2), one fresh 20 s run per goal and arm, solve_new.sh's model and lemma options. CW0 is the
# control; CW9 the control at 40 s, the time-matched control for "control + one weight variant".
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
for a in CW0 CW1 CW2 CW3 CW4 CW5 CW6 CW7 CW9; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
run() { D=$1; T=$2; J=$3; X=$4
python3 -u /project/twee/hints/loop.py sets/wheads300 loops/$D --init loops/LAA.ctx --start 1 --rounds 1 --keep-out -j $J \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout $T \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider $X" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv) $(date +%T)" >> loops/EXP57.pids; }
echo "exp57 start $(date '+%d %T')" >> loops/EXP57.pids
run CW0 20 1 "" &
run CW1 20 1 "--lhs-weight 2" &
run CW2 20 1 "--lhs-weight 8" &
run CW3 20 1 "--depth-weight 0" &
run CW4 20 1 "--depth-weight 5" &
run CW5 20 1 "--var-weight 0.5" &
run CW6 20 1 "--var-weight 1.5" &
run CW7 20 1 "--dup-factor 1" &
run CW9 40 2 "" &
wait
echo "exp57 done $(date '+%d %T')" >> loops/EXP57.pids
