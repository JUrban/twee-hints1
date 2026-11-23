#!/bin/bash
# (23 Nov) The step test bed, batch 2 (notes/2026-11-23-conditional.md): twee's goal and ordering options on
# sets/hardstep300 with COND1's problems (10 earlier siblings, 30 kNN, 5 s), 6 threads, one arm at a time. Starts when
# batch 1 (abs/stepbed1.sh) has written "end" to cond/STEP.done.
cd /project/hintwork
until grep -q "^end" cond/STEP.done 2>/dev/null; do sleep 30; done
run() { A=$1; shift; [ -e cond/STEP_$A ] && { echo "cond/STEP_$A exists"; return; }
  python3 -u /project/twee/hints/exp/condprove.py cond/STEP_$A --only sets/hardstep300 -j 6 --time 5 --sibs 10 --knn 30 "$@" > cond/STEP_$A.log 2>&1
  echo "$A $(date '+%T') $(grep -c "	THM	" cond/STEP_$A/results.tsv) of $(grep -c . cond/STEP_$A/results.tsv)" >> cond/STEP2.done; }
echo "start $(date '+%d %T')" >> cond/STEP2.done
run GH --args "--goal-heuristic"
run HG --args "--hint-goal"
run BG2 --args "--backwards-goal 2"
run FGL --args "--no-flatten-goal --flatten-goal-lightly"
run NFG --args "--no-flatten-goal"
run KW0 --args "--kbo-weight0"
run FLIP --args "--flip-ordering"
run GJB --args "--ground-joining-branch-limit 100"
echo "end $(date '+%d %T')" >> cond/STEP2.done
