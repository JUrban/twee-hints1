#!/bin/bash
# Z7 pair (21 Nov 12:50, notes/2026-11-21-z7-pair.md): today's late-phase default (solve_new.sh's LATE: --retry-class
# --yield-discount 2000 --reexplore 12:0.25 --knn-ctx 10 --head-class) against the 20 Nov system (LATE=), side by side
# on the whole benchmark: as Z6 (abs/z6_test.sh: an empty context, all 51,784 public goals, SCHED=, transfer every 5
# minutes, --knn-refresh 600) but 6 workers each, so that the pair stays near 20 CPUs. Both get today's dispatch
# changes (goal files at first use, the conjecture cache, the knn_at.tsv flush).
cd /project/hintwork
for a in Z7 Z7C; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z7.solve_new.sh
cp loops/Z7.solve_new.sh loops/Z7C.solve_new.sh
( SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600" bash loops/Z7.solve_new.sh sets/all loops/EMPTY loops/Z7 ${J:-6} ${HOURS:-8} > loops/Z7.out 2>&1
  echo "Z7 done $(date +%T)" > loops/Z7.done ) &
( LATE= SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600" bash loops/Z7C.solve_new.sh sets/all loops/EMPTY loops/Z7C ${J:-6} ${HOURS:-8} > loops/Z7C.out 2>&1
  echo "Z7C done $(date +%T)" > loops/Z7C.done ) &
wait
