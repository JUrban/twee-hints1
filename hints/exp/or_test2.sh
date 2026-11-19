#!/bin/bash
# --orig-rate A/B from zero at scale (17 Nov 09:05): ${SET:-sets/half1} (64 of the 129 originals, random seed 17), 6 workers
# each, 2 hours, SCHED= , transfer every 5 minutes, solve_new.sh's default order (--mix 0.1 --fail-order).
# ARM=ORA control, ARM=ORB LOOPARGS=--orig-rate (the original's recent proof rate orders goals within a failure count
# and within each deeper level). Z4's late runs: top fifth by that rate proved 50% against 10% (REPORT 2au).
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="$LOOPARGS" bash loops/$ARM.solve_new.sh ${SET:-sets/half1} loops/EMPTY loops/$ARM ${J:-6} ${HOURS:-2} > loops/$ARM.out 2>&1
touch loops/$ARM.done
