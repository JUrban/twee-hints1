#!/bin/bash
# (20 Nov 19:37) exp44 + exp45 from zero on half2, 6 workers each, 5 hours, started together after Z6
# (notes/2026-11-20-retry-class.md, notes/2026-11-20-yield-discount.md):
#   P2K  solve_new.sh's defaults (the 5-hour control; P2E/P2F ran 2 hours)
#   P2H  + --retry-class                                (exp44)
#   P2J  + --yield-discount 2000 --reexplore 12:0.25    (exp45; 12 CPU h = 2 hours on 6 workers)
cd /project/hintwork
HOURS=5 SET=sets/half2 ARM=P2K LOOPARGS= bash abs/or_test2.sh &
HOURS=5 SET=sets/half2 ARM=P2H LOOPARGS="--retry-class" bash abs/or_test2.sh &
HOURS=5 SET=sets/half2 ARM=P2J LOOPARGS="--yield-discount 2000 --reexplore 12:0.25" bash abs/or_test2.sh &
wait
echo "exp44/45 done $(date +%T)" > loops/exp4445.done
