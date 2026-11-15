#!/bin/bash
# rule-penalty sweep at 20 abstract s on nil3_31 150 (sets/u3n150), online from V2base, rm4t, 6 lemmas + 10 subset-kNN:
# baseline N3l6 = 76 (threshold 0.1, penalty 2).
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 10 --lemma-subsets"
A="--abstract-time 2000 --max-cpu 200"
for p in 5 20; do
  python3 /project/twee/hints/loop.py sets/u3n150 loops/N3p$p $C $M --model-args "--rule-threshold 0.1 --rule-penalty $p" --args="$A" > loops/N3p$p.log 2>&1
  echo "N3p$p $(grep -c THM loops/N3p$p/r1/results.tsv) $(date +%T)" | tee loops/N3p$p.done
done
