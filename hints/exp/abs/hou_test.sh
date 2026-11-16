#!/bin/bash
# HO8 with today's public context (16 Nov 22:05): as HO8b (sets/ho8, solve_new.sh's defaults, 4 workers, 1 hour,
# EXCLUDE=originals) but CTX=loops/HOX = loops/UL now minus the proofs known to use a ho8 goal (abs/freshctx.py).
# With LVU (rp3) it gives the 11-original holdout figure with today's context. ARM=HO8U.
cd /project/hintwork
[ -e loops/HOX ] || python3 abs/freshctx.py sets/ho8 loops/HOX > loops/$ARM.ctxlog 2>&1
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
EXCLUDE=originals LOOPARGS= bash loops/$ARM.solve_new.sh sets/ho8 loops/HOX loops/$ARM 4 ${HOURS:-1} > loops/$ARM.out 2>&1
touch loops/$ARM.done
