#!/bin/bash
# --fail-order over an hour (17 Nov 05:15): sets/rp3 from zero as LVZ (SCHED= , 4 workers, 1 hour; 890 at 60 min) and
# MX60 (+ --mix 0.25), with LOOPARGS="--mix ${MIX:-0.25} --fail-order". Production stays paused meanwhile.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= LOOPARGS="--mix ${MIX:-0.25} --fail-order" bash loops/$ARM.solve_new.sh sets/rp3 loops/EMPTY loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done
