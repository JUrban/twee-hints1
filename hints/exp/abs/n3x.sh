#!/bin/bash
# Speed check of twee-e27 (fingerprint overlap index + interreduce filter) against N3l6 (e22, 76 solved):
# same config: sets/u3n150, 20 abstract s, online, 6 sibling lemmas + 10 subset kNN, rm4t.
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
python3 /project/twee/hints/loop.py sets/u3n150 loops/N3x6 $C --twee /project/bin/twee-e27 $M --lemmas 6 --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3x6.log 2>&1
echo "N3x6 $(grep -c THM loops/N3x6/r1/results.tsv) $(date +%T)" | tee loops/N3x6.done
