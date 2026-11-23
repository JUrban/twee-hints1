#!/bin/bash
# (18 Nov 17:52) p9c with 4 workers instead of 2 (log P9C4.log). By the portfolio's ratio rule it is the best deep
# member per CPU: 1.98 new proofs per CPU hour on the walls twee's chain failed (exp16), 1.44 live from 16:46 to 17:49
# (3 proofs in 126 runs), against 1.16 for production's 80 s chain level. Its 225 queued stalled goals would take
# 2 workers about 2 hours. Restarting keeps loops/P9C/results.tsv, from which the live mode reloads what it tried.
# (18 Nov) Prover9 side worker with chain hints (exp16: on the 107 walls at 60 s, Prover9 with the chain proved 4,
# with the pool 2, both in 1.8 CPU h; 3 of the chain's 4 were walls twee failed in exp11). p9twee.py --live takes
# the goals twee is stalled on (last deep run and a fresh run of the round failed), nearest to a proof first
# (proof lines, at most 80), retries a goal when its nearest proven goal below changes or its original's pool grows
# 1.25x, and writes proofs straight into loops/UL (hints file, then a solved.tsv row), where loop.py --sync picks
# them up. Hints: the goal's chain (sibchain.py, chain_records2.tsv) instead of the 15 Nov pool.
# Usage: bash abs/p9c.sh [PID]   (waits for PID to end first)
cd /project/hintwork
if [ -n "$1" ]; then while kill -0 $1 2>/dev/null; do sleep 60; done; fi
echo "P9C start $(date +%T)" >> loops/P9C.start
python3 -u /project/twee/hints/p9twee.py --live loops/UL loops/P9C -j 4 --timeout 60 \
  --chain /project/hintwork/chain_records2.tsv > loops/P9C4.log 2>&1
echo "P9C: $(tail -1 loops/P9C4.log) $(date +%T)" | tee loops/P9C4.done
