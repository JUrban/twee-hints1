#!/bin/bash
# SG2 arm of abs/sg.sh, restarted alone (20:55): the first start crashed on a goal-info cache race with SG1 (fixed 873e305).
cd /project/hintwork
C="--init loops/ULsJ --start 1 --rounds 1 --keep-out -j 2 --pool original --online --wall-factor 15 --resume"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22"
python3 /project/twee/hints/loop.py sets/sg2 loops/SG2 $C $M $L --timeout 60 --args="--abstract-time 2000 --max-cpu 600 --no-resume-requeue --no-eqhint-consider" > loops/SG2.log 2>&1
echo "SG2 $(grep -c THM loops/SG2/r1/results.tsv)/48 $(date +%T)" | tee loops/SG2.done
