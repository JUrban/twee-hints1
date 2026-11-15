#!/bin/bash
# After abl3.sh (U3k20.done): lemma count on a second original (first 150 unsolved nil3_31 goals, sets/u3n150):
# N3l3 (3 siblings) vs N3l6 (6 siblings); then the rm6t runs of abl4.sh (U3zm, U3zf).
# All 20 abstract s, online, from V2base, rm4t unless noted.
until [ -s /project/hintwork/loops/U3k20.done ]; do sleep 60; done
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
for k in 3 6; do
  python3 /project/twee/hints/loop.py sets/u3n150 loops/N3l$k $C $M --lemmas $k --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3l$k.log 2>&1
  echo "N3l$k $(grep -c THM loops/N3l$k/r1/results.tsv) $(date +%T)" | tee loops/N3l$k.done
done
B="python3 /project/twee/hints/loop.py sets/u3a189"
M="--model --model-fixed /project/hintwork/models/rm6t.bin,/project/hintwork/models/rm6t.vocab --model-theory"
$B loops/U3zm $C $M --max-hints 0 --rerun-unhinted --args="$A" > loops/U3zm.log 2>&1
echo "U3zm $(grep -c THM loops/U3zm/r1/results.tsv) $(date +%T)" | tee loops/U3zm.done
$B loops/U3zf $C $M --lemmas 3 --lemma-knn 10 --lemma-subsets --args="$A" > loops/U3zf.log 2>&1
echo "U3zf $(grep -c THM loops/U3zf/r1/results.tsv) $(date +%T)" | tee loops/U3zf.done
