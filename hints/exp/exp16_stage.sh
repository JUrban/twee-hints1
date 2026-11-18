#!/bin/bash
# exp16/stage.sh PID: wait for PID (exp14's runner) to end, then Prover9 on the 107 walls at 60 s, pool and chain
# hints side by side, 2 workers each, in UL's proven state at 10:29 (the first 45,414 rows of solved.tsv).
cd /project/hintwork/exp16
while kill -0 $1 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) start P, Q" >> stage.log
P9=/project/twee/hints/p9twee.py; UL=/project/hintwork/loops/UL
python3 $P9 walls107 $UL out_P --timeout 60 -j 2 --solved-rows 45414 > P.out 2>&1 &
python3 $P9 walls107 $UL out_Q --timeout 60 -j 2 --solved-rows 45414 --chain /project/hintwork/chain_records.tsv > Q.out 2>&1 &
wait
echo "$(date +%H:%M) end P, Q" >> stage.log
