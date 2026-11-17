#!/bin/bash
# The whole benchmark from zero with --mix (17 Nov 03:20): as abs/z1_test.sh (Z1, from 00:56, stopped at 126 minutes
# with 36,760) plus loop.py --mix 0.1. In Z1 the near retries took every slot: all 34,579 runs at 5 s, and 12,998 of
# its 15,062 unsolved goals never ran (6,080 of production's 8,116 extra proofs are on them). --mix 0.1 keeps 2 of
# the 12 workers each for goals beyond the retry gaps (and never run) and for deeper levels while they have goals,
# and gives the other slots to the kind with the most proofs per run second lately. 12 workers, 10 hours, SCHED=,
# transfer every 5 minutes. On rp3 (15 minutes, 4 workers) --mix 0.1 gave 831 against PE1's 830.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z2.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--mix ${MIX:-0.1}" bash loops/Z2.solve_new.sh sets/all loops/EMPTY loops/Z2 ${J:-12} ${HOURS:-10} > loops/Z2.out 2>&1
touch loops/Z2.done
