#!/bin/bash
# The replay with today's public context (as abs/lvu_test.sh, LVU 1,085 of 1,320 in 1 hour with the learned
# scheduler), without the scheduler and with --mix 0.25 --fail-order (17 Nov 06:20). sets/rp3, CTX=loops/ULX,
# EXCLUDE=originals, 4 workers, 1 hour. ARM=LVF. Runs a private copy of solve_new.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
EXCLUDE=originals SCHED= LOOPARGS="--mix ${MIX:-0.25} --fail-order" \
  bash loops/$ARM.solve_new.sh sets/rp3 ${CTX:-loops/ULX} loops/$ARM 4 ${HOURS:-1} > loops/$ARM.out 2>&1
touch loops/$ARM.done
