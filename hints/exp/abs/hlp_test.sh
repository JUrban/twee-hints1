#!/bin/bash
# Hints from the kNN lemmas' proofs (16 Nov 11:35; loop.py --hint-lemma-proofs F: the proof steps of each of the 30
# kNN lemmas, mostly other originals' proven goals, as hints with score factor F after the own pool; at most 300 per
# proof). As abs/knn_test.sh (30 kNN lemmas, ULsZ, fresh 20 s; control KN30 6/150): ARM=KH01 F=0.1, KH001 F=0.01
# (the own pool's factor).
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/${SET:-unsol150} loops/$ARM --init loops/ULsZ --start 1 --rounds 1 --keep-out -j ${J:-2} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn ${K:-30} --lemma-subsets --lemma-after --pool original --hint-lemma-proofs $F --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/$(wc -l < sets/${SET:-unsol150}) $(date +%T)" | tee loops/$ARM.done
