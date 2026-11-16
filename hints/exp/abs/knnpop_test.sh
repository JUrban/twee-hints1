#!/bin/bash
# kNN lemmas weighted by use (16 Nov 08:15; loop.py --lemma-pop B --lemma-uses loops/UL: similarity x (1 + B log(1 +
# number of production proofs that used the lemma)), the 150 test goals' own proofs left out of the counts). As
# abs/knn_test.sh with 30 kNN lemmas (control KN30, 6/150): ARM=KP03 B=0.3 (a quarter of the top 30 changes),
# KP10 B=1.0 (41% change).
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/${SET:-unsol150} loops/$ARM --init loops/ULsZ --start 1 --rounds 1 --keep-out -j ${J:-2} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn ${K:-30} --lemma-pop $B --lemma-uses loops/UL --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/$(wc -l < sets/${SET:-unsol150}) $(date +%T)" | tee loops/$ARM.done
