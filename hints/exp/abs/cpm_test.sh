#!/bin/bash
# The rule model orders twee's queue (16 Nov 11:20; twee-e42 --cp-model-factor F: each critical pair's score x F ** q,
# q = rm4t's probability that it is a proof rule; F = 1 is off, as e41). As abs/knn_test.sh (30 kNN lemmas, ULsZ,
# fresh 20 s): ARM=CPA F=1 (control on e42), CPB F=0.1, ...; SET defaults to unsol150.
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/${SET:-unsol150} loops/$ARM --init loops/ULsZ --start 1 --rounds 1 --keep-out -j ${J:-2} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn ${K:-30} --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e42 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider --cp-model-factor ${F:-1}" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/$(wc -l < sets/${SET:-unsol150}) $(date +%T)" | tee loops/$ARM.done
