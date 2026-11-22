#!/bin/bash
# (22 Nov 03:00) A late-phase A/B arm: the goals a from-zero run left unsolved, with that run's proofs as the
# context (notes/2026-11-22-late-ab.md). ${SET:-sets/late2} (the 3,817 half2 goals Z7 did not prove in 8 hours),
# CONTEXT ${CTX:-loops/Z7} (Z7's 43,769 proofs), ${J:-4} workers, ${HOURS:-3} hours, SCHED= , transfer every 5
# minutes, solve_new.sh's defaults; LOOPARGS and PG as in abs/or_test2.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="$LOOPARGS" bash loops/$ARM.solve_new.sh ${SET:-sets/late2} ${CTX:-loops/Z7} loops/$ARM ${J:-4} ${HOURS:-3} > loops/$ARM.out 2>&1
touch loops/$ARM.done
