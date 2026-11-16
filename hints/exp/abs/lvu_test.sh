#!/bin/bash
# The replay with today's public context (16 Nov 21:55). The 4-hour replays level off near 950 of 1,320 against
# production's 1,111, and 45 of 54 traceable production proofs of the gap goals use kNN lemmas from other originals'
# goals proven after loops/ALL (13 Nov, 32k proofs). CTX=loops/ULX: loops/UL at 21:52 (44.8k) minus 46 proofs known
# to use an rp3 goal (a kNN lemma named in a kept output, or a transfer source; loops/ULX/excluded.tsv). As LVS2
# (940 with loops/ALL): solve_new.sh's defaults, 4 workers, 1 hour. ARM=LVU. Runs a private copy of solve_new.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
EXCLUDE=originals LOOPARGS= \
  bash loops/$ARM.solve_new.sh sets/rp3 ${CTX:-loops/ULX} loops/$ARM 4 ${HOURS:-1} > loops/$ARM.out 2>&1
touch loops/$ARM.done
