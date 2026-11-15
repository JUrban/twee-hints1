#!/bin/bash
# Scheduling probe (14 Nov 20:50): proofs per CPU-hour of (a) gap-2 goals at L1 (resume their L0 state +60 abstract s)
# against (b) gap-1 goals that failed L1 at L2 (resume their L1 state +240 s). Samples sets/sg2 (48 of 697) and
# sets/sg1 (32 of 762), seed 7; states copied from loops/UL; snapshot loops/ULsJ (41,473 proofs). Production config
# (rm4t fixed, 6 lemmas + 10 kNN, --no-resume-requeue --no-eqhint-consider), 2 workers each.
cd /project/hintwork
C="--init loops/ULsJ --start 1 --rounds 1 --keep-out -j 2 --pool original --online --wall-factor 15 --resume"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22"
python3 /project/twee/hints/loop.py sets/sg2 loops/SG2 $C $M $L --timeout 60 --args="--abstract-time 2000 --max-cpu 600 --no-resume-requeue --no-eqhint-consider" > loops/SG2.log 2>&1 &
python3 /project/twee/hints/loop.py sets/sg1 loops/SG1 $C $M $L --timeout 240 --args="--abstract-time 2000 --max-cpu 2400 --no-resume-requeue --no-eqhint-consider" > loops/SG1.log 2>&1 &
wait
echo "SG2 $(grep -c THM loops/SG2/r1/results.tsv)/48 SG1 $(grep -c THM loops/SG1/r1/results.tsv)/32 $(date +%T)" | tee loops/SG.done
