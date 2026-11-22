#!/bin/bash
# Z8 (22 Nov, notes/2026-11-22-z8.md): the system as it stands from zero on the whole benchmark, one arm: solve_new.sh's
# defaults (LATE with --floor-ratio 20 since 21 Nov 23:51, exp52), as Z7 (abs/z7pair.sh: an empty context, all
# 51,784 goals, SCHED=, transfer every 5 minutes, --knn-refresh 600, 6 workers, 8 hours). Against Z7's curve
# (cross-time): exp52's early gain should show at 1-2 hours, and the 8-hour count says whether the floors that wait
# cost anything late.
cd /project/hintwork
[ -e loops/Z8 ] && { echo "loops/Z8 exists"; exit 1; }
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z8.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600" bash loops/Z8.solve_new.sh sets/all loops/EMPTY loops/Z8 ${J:-6} ${HOURS:-8} > loops/Z8.out 2>&1
echo "Z8 done $(date +%T)" > loops/Z8.done
