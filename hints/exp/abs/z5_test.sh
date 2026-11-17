#!/bin/bash
# Z5 (17 Nov): Z4 (abs/z4_test.sh: solve_new.sh's defaults, --mix 0.1 --fail-order, 12 workers, transfer every 5 min)
# with today's changes: twee-e44 (= e43 + incremental hint renormalisation, -11% CPU) / e43 (no state for a proved goal: proved runs a third faster, ORE/ORF 10,282/10,094 vs
# 9,303/9,575 at 10 min on half1), the 20 s level (5,20,80,320: ORC 18,552 vs 18,504/18,319 at 2 h) and
# $LOOPARGS (--no-fresh-states if ORH beats ORG). All 51,784 public goals from zero, 10 hours.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z5.solve_new.sh
SCHED= XEVERY=300 TWEE=${TWEE:-/project/bin/twee-e44} CASCADE=${CASCADE:-5,20,80,320} LOOPARGS="$LOOPARGS" \
  bash loops/Z5.solve_new.sh sets/all loops/EMPTY loops/Z5 ${J:-12} ${HOURS:-10} > loops/Z5.out 2>&1
touch loops/Z5.done
