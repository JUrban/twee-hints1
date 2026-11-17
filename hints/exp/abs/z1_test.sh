#!/bin/bash
# The whole benchmark from zero again, with the faster dispatcher (17 Nov 01:00): as abs/z0_test.sh (Z0, from 23:49),
# whose dispatcher kept only 2.7-5.3 of its 12 workers busy for 40 minutes: the scheduling pass re-scanned all 51,784
# goals after every run (134 of the main thread's 180 s in a 3-minute test). loop.py --pass-every 1 (solve_new.sh's
# default now) makes the full pass at most once a second: 1,454 runs against 1,043 in the first minute of the test.
# Z0's first 50 minutes stay as the comparison. 12 workers, 10 hours, SCHED=, transfer every 5 minutes.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z1.solve_new.sh
SCHED= XEVERY=300 LOOPARGS= bash loops/Z1.solve_new.sh sets/all loops/EMPTY loops/Z1 ${J:-12} ${HOURS:-10} > loops/Z1.out 2>&1
touch loops/Z1.done
