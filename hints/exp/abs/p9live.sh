#!/bin/bash
# Prover9 side worker for the production loop (15 Nov): stalled goals of loops/UL (fresh and resume failed in the
# latest round, within 80 proof lines), nearest first; Prover9 with the original's twee pool as hints and 6 proven
# siblings either side as assumptions, 60 s; proofs go straight into loops/UL (UL reads them with --sync 60).
# On sets/st79u (stalled in twee: settings portfolio, cross-original pools, rm7t, climber, 80 s all 0) the batch
# probe loops/P9T proved aK2_eq_aK3_r__goal_241 in 44 s.
cd /project/hintwork
python3 -u /project/twee/hints/p9twee.py --live loops/UL loops/P9L -j ${J:-3} --timeout ${T:-60} > loops/P9L.log 2>&1
