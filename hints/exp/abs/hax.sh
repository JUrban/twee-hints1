#!/bin/bash
# frequent pool hints as axioms (--hint-axioms K:F) on nil3_31 150 (sets/u3n150), 20 abstract s, online, from V2base,
# rm4t, 6 sibling lemmas + 10 subset-kNN: baseline N3l6 = 76.
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 10 --lemma-subsets"
A="--abstract-time 2000 --max-cpu 200"
for v in 10:20 50:10; do
  d=N3h$(echo $v | tr ':' '_')
  python3 /project/twee/hints/loop.py sets/u3n150 loops/$d $C $M --hint-axioms $v --args="$A" > loops/$d.log 2>&1
  echo "$d $(grep -c THM loops/$d/r1/results.tsv) $(date +%T)" | tee loops/$d.done
done
