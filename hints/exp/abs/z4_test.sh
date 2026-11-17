#!/bin/bash
# Z3 again with the faster pass (17 Nov 04:55): loop.py waits at least 8 times the last full pass between full passes
# (Z3 kept 5-7 of its 12 workers busy; its pass took 0.2-0.35 s; stopped at 24 min). Z3 (abs/z3_test.sh) = Z2
# (--mix 0.1) + --fail-order. 12 workers, 10 hours, SCHED=, transfer every 5 minutes.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z4.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--mix ${MIX:-0.1} --fail-order" bash loops/Z4.solve_new.sh sets/all loops/EMPTY loops/Z4 ${J:-12} ${HOURS:-10} > loops/Z4.out 2>&1
touch loops/Z4.done
