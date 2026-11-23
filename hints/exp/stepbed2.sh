#!/bin/bash
# (23 Nov) After the step test bed's batch 1 (abs/stepbed1.sh writes "end" to cond/STEP.done):
# 1. COND2: COND1 again with 30 earlier siblings (batch 1's SIB30 proved 41 of 300 hard goals, all with a sibling more
#    than 10 back), all unsolved goals, earlier siblings only (the blocking graph stays well-founded); cond/COND2.
# 2. Batch 2: twee's goal and ordering options on sets/hardstep300 with SIB30's problems (30 earlier siblings, 30 kNN,
#    5 s), 6 threads, one arm at a time, into cond/STEP_<arm>.
cd /project/hintwork
until grep -q "^end" cond/STEP.done 2>/dev/null; do sleep 30; done
if [ ! -e cond/COND2 ]; then
  echo "COND2 start $(date '+%d %T')" > cond/COND2.pids
  python3 -u /project/twee/hints/exp/condprove.py cond/COND2 -j 6 --time 5 --sibs 30 --knn 30 > cond/COND2.log 2>&1
  echo "COND2 done $(date '+%d %T') exit $?" >> cond/COND2.pids
fi
run() { A=$1; shift; [ -e cond/STEP_$A ] && { echo "cond/STEP_$A exists"; return; }
  python3 -u /project/twee/hints/exp/condprove.py cond/STEP_$A --only sets/hardstep300 -j 6 --time 5 --sibs 30 --knn 30 "$@" > cond/STEP_$A.log 2>&1
  echo "$A $(date '+%T') $(grep -c "	THM	" cond/STEP_$A/results.tsv) of $(grep -c . cond/STEP_$A/results.tsv)" >> cond/STEP2.done; }
echo "start $(date '+%d %T')" >> cond/STEP2.done
run S30KNN29 --knn 29
run S30GH --args "--goal-heuristic"
run S30HG --args "--hint-goal"
run S30BG2 --args "--backwards-goal 2"
run S30FGL --args "--no-flatten-goal --flatten-goal-lightly"
run S30KW0 --args "--kbo-weight0"
run S30FLIP --args "--flip-ordering"
run S30GJB --args "--ground-joining-branch-limit 100"
echo "end $(date '+%d %T')" >> cond/STEP2.done
