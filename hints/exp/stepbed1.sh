#!/bin/bash
# (23 Nov) The step test bed (notes/2026-11-23-conditional.md, "Step test bed"): sets/hardstep300, 300 of COND1's hard
# goals (seed 23), exp/condprove.py with one change per arm, 6 threads each, one arm at a time, into cond/STEP_<arm>.
# COND1's setting (10 earlier siblings, 30 kNN, 5 s) proved none of them.
cd /project/hintwork
run() { A=$1; shift; [ -e cond/STEP_$A ] && { echo "cond/STEP_$A exists"; return; }
  python3 -u /project/twee/hints/exp/condprove.py cond/STEP_$A --only sets/hardstep300 -j 6 "$@" > cond/STEP_$A.log 2>&1
  echo "$A $(date '+%T') $(grep -c "	THM	" cond/STEP_$A/results.tsv) of $(grep -c . cond/STEP_$A/results.tsv)" >> cond/STEP.done; }
echo "start $(date '+%d %T')" >> cond/STEP.done
run KNN29 --time 5 --sibs 10 --knn 29
run SIB30 --time 5 --sibs 30 --knn 30
run AFT10 --time 5 --sibs 10 --knn 30 --after 10
run KNN100 --time 5 --sibs 10 --knn 100
run SIB3 --time 5 --sibs 3 --knn 30
run T20 --time 20 --sibs 10 --knn 30
echo "end $(date '+%d %T')" >> cond/STEP.done
