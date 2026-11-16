#!/bin/bash
# The final system from zero on the whole public benchmark (16 Nov 22:15): every goal of sets/all (51,784), an empty
# context (loops/EMPTY), solve_new.sh's options without the learned scheduler (SCHED=: from zero it needs
# --sweep-first, which at this scale would run every goal once before any retry; without it the cascade's own order,
# nearest a proven goal first, scales as in production before 15 Nov), the transfer every 5 minutes (as production's
# XFL; its scans grow with the proofs), 12 workers, 10 hours. Proofs found here that production lacks can be merged
# into loops/UL later. Runs a private copy of solve_new.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/Z0.solve_new.sh
SCHED= XEVERY=300 LOOPARGS= bash loops/Z0.solve_new.sh sets/all loops/EMPTY loops/Z0 ${J:-12} ${HOURS:-10} > loops/Z0.out 2>&1
touch loops/Z0.done
