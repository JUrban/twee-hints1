#!/bin/bash
# Z7 (21 Nov, after exp48/exp49): the from-zero system with the late-phase winners on the whole benchmark, against Z6
# (abs/z6_test.sh: 44,095 at 8 hours). As Z6 (solve_new.sh's defaults, an empty context, all 51,784 public goals, 12
# workers, 8 hours, SCHED=, transfer every 5 minutes, --knn-refresh 600) plus WIN (from the environment, may be empty): the options
# exp44/45 (--retry-class; --yield-discount 2000 --reexplore 12:0.25), exp48 (--knn-ctx 10 --head-class) and exp49
# (--quick 1) kept (notes/2026-11-21-late-combo.md, notes/2026-11-21-quick-first.md).
cd /project/hintwork
# (21 Nov 11:05) WIN may be empty once solve_new.sh's defaults (LATE) hold the winners
[ -e loops/Z7 ] && { echo "loops/Z7 exists"; exit 1; }
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z7.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600 $WIN" bash loops/Z7.solve_new.sh sets/all loops/EMPTY loops/Z7 ${J:-12} ${HOURS:-8} > loops/Z7.out 2>&1
echo "Z7 done $(date +%T)" > loops/Z7.done
