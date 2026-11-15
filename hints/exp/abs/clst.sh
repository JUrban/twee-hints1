#!/bin/bash
# Breakthrough probe (15 Nov 06:05): sketch climbing (as CL5: 8 unproven siblings + 8 kNN, --fill 3) on sets/st79,
# goals stalled in their context (no L0 variant proves them at 20 s), from snapshot loops/ULsM, 2 workers.
# Against: fresh 80 s (T=80 V=base bash abs/port.sh sets/st79).
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/st79 loops/CLST --m 8 --knn 8 --runs 12 --sketch-time 5 --final-time 20 --fill 3 -j 2 -- \
  --init loops/ULsM --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e37 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CLST.log 2>&1
echo "CLST $(tail -1 loops/CLST.log) $(date +%T)" | tee loops/CLST.done
