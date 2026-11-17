#!/bin/bash
# --fail-reset over an hour (17 Nov 07:25): sets/rp3 from zero as FO60 (SCHED= , 4 workers, 1 hour, --mix 0.25
# --fail-order; 891) plus --fail-reset: a goal's failures count from the last change of the nearest proven goal below.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= LOOPARGS="--mix ${MIX:-0.25} --fail-order --fail-reset" bash loops/$ARM.solve_new.sh sets/rp3 loops/EMPTY loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done
