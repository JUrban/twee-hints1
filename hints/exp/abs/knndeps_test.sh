#!/bin/bash
# MaSh-style kNN lemmas (16 Nov 08:30; loop.py --lemma-deps W: a lemma scores the similarity of each of the 50 nearest
# proven goals it is, plus W x similarity x idf / sqrt(#deps) for each nearest proven goal whose proof has the
# lemma's equation as a step; lemmas.proof_deps over the 44k stored proofs, 20 s). As abs/knn_test.sh with 30 kNN
# lemmas (control KN30, 6/150): ARM=KD10 W=1.0 (top 30 23% changed), KD30 W=3.0 (40% changed).
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/${SET:-unsol150} loops/$ARM --init loops/ULsZ --start 1 --rounds 1 --keep-out -j ${J:-2} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn ${K:-30} --lemma-deps $W --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/$(wc -l < sets/${SET:-unsol150}) $(date +%T)" | tee loops/$ARM.done
