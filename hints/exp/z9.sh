#!/bin/bash
# Z9 (22 Nov; notes/2026-11-23-z9.md, written at launch): the system as it stands from zero on the whole benchmark,
# one arm, as Z8 (abs/z8.sh: an empty context, all 51,784 goals, SCHED=, transfer every 5 minutes, --knn-refresh 600,
# 6 workers, 8 hours): solve_new.sh's defaults, now with --knn-drift 5 in LATE (exp55) and whatever exp60 adopts.
# A measurement of the system against Z8's curve, not an A/B (runs at different times differ by up to about 400).
cd /project/hintwork
[ -e loops/Z9 ] && { echo "loops/Z9 exists"; exit 1; }
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z9.solve_new.sh
# (22 Nov) CPUSET: whole cores on both sockets, apart from production's (abs/pin_exp60b.sh gave it 21-27,49-55)
SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600 ${Z9ARGS:-}" taskset -c "${CPUSET:-0-20,28-48}" bash loops/Z9.solve_new.sh sets/all loops/EMPTY loops/Z9 ${J:-6} ${HOURS:-8} > loops/Z9.out 2>&1
echo "Z9 done $(date +%T)" > loops/Z9.done
