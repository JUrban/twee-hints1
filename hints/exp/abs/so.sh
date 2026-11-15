#!/bin/bash
# Stalled-goal probe (14 Nov 21:40): the 32 gap-1 goals of sets/sg1 failed L1 (resume to 80 abstract s). SG1 resumes
# them to 320 s (+240). SO restarts them fresh for 80 s with another term ordering (--p9-orders 4, ordering 1),
# same snapshot loops/ULsJ and config otherwise. Proofs per CPU-hour decide what the cascade does with stalled goals.
cd /project/hintwork
C="--init loops/ULsJ --start 1 --rounds 1 --keep-out -j 2 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22"
python3 /project/twee/hints/loop.py sets/sg1 loops/SO $C $M $L --timeout 80 --p9-orders 4 --p9-order-offset 1 \
  --args="--abstract-time 2000 --max-cpu 800 --no-eqhint-consider" > loops/SO.log 2>&1
echo "SO $(grep -c THM loops/SO/r1/results.tsv)/32 $(date +%T)" | tee loops/SO.done
