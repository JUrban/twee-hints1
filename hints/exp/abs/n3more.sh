#!/bin/bash
# nil3_31 150 (sets/u3n150), 20 abstract s, online, from V2base, rm4t: N3l3 62, N3l6 76.
# N3l10: 10 nearest below; N3l6a: 6 nearest on either side (--lemma-after).
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
python3 /project/twee/hints/loop.py sets/u3n150 loops/N3l10 $C $M --lemmas 10 --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3l10.log 2>&1
echo "N3l10 $(grep -c THM loops/N3l10/r1/results.tsv) $(date +%T)" | tee loops/N3l10.done
python3 /project/twee/hints/loop.py sets/u3n150 loops/N3l6a $C $M --lemmas 6 --lemma-after --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3l6a.log 2>&1
echo "N3l6a $(grep -c THM loops/N3l6a/r1/results.tsv) $(date +%T)" | tee loops/N3l6a.done
