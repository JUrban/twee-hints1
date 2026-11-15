#!/bin/bash
# Hint consider-emulation off (14 Nov 19:50): on one 30 abstract s run it costs 26% of the CPU (59.5 -> 44.1 s user)
# and matches no more hints (973 vs 981). N3c = N3x6 (76 solved, e27) + --no-eqhint-consider, twee-e34.
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --keep-out -j 3 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider"
python3 /project/twee/hints/loop.py sets/u3n150 loops/N3c $C --twee /project/bin/twee-e34 $M --lemmas 6 --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3c.log 2>&1
echo "N3c $(grep -c THM loops/N3c/r1/results.tsv) $(date +%T)" | tee loops/N3c.done
