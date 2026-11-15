#!/bin/bash
# Control for the live climber (15 Nov 01:04): fresh 20 s (as UL L0) on the 102 targets CLV climbed first (31 solved),
# from a UL snapshot without the climber's proofs (loops/ULsL).
# Control 2 (14 Nov 22:20): fresh 20 s, DEFAULT ordering (does the gain need 80 s?). Stalled-goal probe (14 Nov 21:40): the 32 gap-1 goals of sets/sg1 failed L1 (resume to 80 abstract s). SG1 resumes
# them to 320 s (+240). SO restarts them fresh for 80 s with another term ordering (--p9-orders 4, ordering 1),
# same snapshot loops/ULsL and config otherwise. Proofs per CPU-hour decide what the cascade does with stalled goals.
cd /project/hintwork
C="--init loops/ULsL --start 1 --rounds 1 --keep-out -j 2 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22"
python3 /project/twee/hints/loop.py sets/clv1 loops/FV $C $M $L --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/FV.log 2>&1
echo "FV $(grep -c THM loops/FV/r1/results.tsv)/102 $(date +%T)" | tee loops/FV.done
