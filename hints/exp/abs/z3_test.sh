#!/bin/bash
# The whole benchmark from zero with --fail-order (17 Nov 04:30): as abs/z2_test.sh (Z2: --mix 0.1; 33,539 at 60 min
# against Z1's 34,181, stopped at 65 min) plus loop.py --fail-order: the fresh runs in one list, goals with the fewest
# failed fresh runs first (near before far within a count). In Z1's second hour first runs proved 51% (365 proofs per
# run hour), repeats 4-6% (17-29) on 61% of the time. rp3 from zero, 2 workers, 2.4 min: 617 against 383 (--mix alone).
# 12 workers, 10 hours, SCHED=, transfer every 5 minutes.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z3.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--mix ${MIX:-0.1} --fail-order" bash loops/Z3.solve_new.sh sets/all loops/EMPTY loops/Z3 ${J:-12} ${HOURS:-10} > loops/Z3.out 2>&1
touch loops/Z3.done
