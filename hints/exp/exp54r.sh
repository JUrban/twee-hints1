#!/bin/bash
# exp54r (22 Nov 10:59, notes/2026-11-22-late-ab.md): the replica pair of exp54's control, for the late design's noise
# (exp54's rule: within ±50, a replica pair of the control comes before any decision). LAC and LAD are both LAA's
# command (solve_new.sh's defaults, abs/late_test.sh, sets/late2, loops/Z7's context, 4 workers each, 3 hours), side by
# side. loop.py now has --knn-drift (94d5ccf, default off).
cd /project/hintwork
for a in LAC LAD; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
diff -q <(sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh) loops/LAA.solve_new.sh > /dev/null \
  || { echo "solve_new.sh differs from LAA's"; exit 1; }
ARM=LAC LOOPARGS="" nohup bash abs/late_test.sh > /dev/null 2>&1 &
echo "LAC $! $(date +%T)" >> loops/EXP54R.pids
ARM=LAD LOOPARGS="" nohup bash abs/late_test.sh > /dev/null 2>&1 &
echo "LAD $! $(date +%T)" >> loops/EXP54R.pids
wait
echo "exp54r done $(date +%T)" >> loops/EXP54R.pids
