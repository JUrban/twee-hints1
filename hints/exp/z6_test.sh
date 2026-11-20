#!/bin/bash
# Z6 (20 Nov, after exp43): today's from-zero system on the whole benchmark, the long run (notes/2026-11-20-z6.md).
# solve_new.sh's defaults (twee-pg61, cascade 5,40,80,160,320 with chain hints, the explored 5 s/80 s portfolio,
# GIVEN=1: the derived-rule transfer) with an empty context on all 51,784 public goals, 12 workers, 8 hours, SCHED=,
# transfer every 5 minutes: as Z4 (abs/z4_test.sh, the 17 Nov system: 37,713 at 2 h, 38,044 at about 4 h). The half
# tests cannot use the other half's kNN lemmas (notes/2026-11-20-half-gap.md); this one can. GIVENARGS (from the
# environment) as exp43 decides. One change from the defaults: --knn-refresh 600 (production's; the default 1800 s,
# or 300 new proofs, delays each kNN cascade step by up to 30 minutes once proofs come slowly).
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z6.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--knn-refresh 600 $LOOPARGS" bash loops/Z6.solve_new.sh sets/all loops/EMPTY loops/Z6 ${J:-12} ${HOURS:-8} > loops/Z6.out 2>&1
echo "Z6 done $(date +%T)" > loops/Z6.done
