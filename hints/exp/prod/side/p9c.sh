#!/bin/bash
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
python3 -u /project/twee/hints/p9twee.py --live loops/UL loops/P9C -j 2 --timeout 60 \
  --chain /project/hintwork/chain_records2.tsv > loops/P9C.log 2>&1
echo "P9C: $(tail -1 loops/P9C.log) $(date +%T)" | tee loops/P9C.done
