#!/bin/bash
# Four hours from scratch (16 Nov 19:00): how fast the pipeline approaches production's 1,111 of 1,320 (sets/rp3,
# 3.5 days of whole-benchmark loops). ARM=LV4 CTX=loops/ALL (clean public context), ARM=LZ4 CTX=loops/EMPTY (from
# zero); 4 workers, transfer every 2 minutes; LOOPARGS as abs/lvs_test.sh if the scheduler wins at 1 hour.
# Runs a private copy of solve_new.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
LOOPARGS="$LOOPARGS" bash loops/$ARM.solve_new.sh sets/rp3 $CTX loops/$ARM 4 ${HOURS:-4} > loops/$ARM.out 2>&1
touch loops/$ARM.done
