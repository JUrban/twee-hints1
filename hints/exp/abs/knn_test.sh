#!/bin/bash
# How many kNN lemmas (16 Nov 06:50): production's proofs use kNN lemmas of every rank almost equally (rank 0 in 1,686
# of 2,755 proved runs, rank 9 in 1,053), so 10 may be too few. Fresh 20 s on sets/unsol150 (random unsolved goals of
# ULsZ) from loops/ULsZ; ARM=KN10 K=10 (control), KN20 K=20, KN30 K=30; 07:50: KN60 K=60, KN100 K=100.
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/${SET:-unsol150} loops/$ARM --init loops/ULsZ --start 1 --rounds 1 --keep-out -j ${J:-2} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn ${K:-10} --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/$(wc -l < sets/${SET:-unsol150}) $(date +%T)" | tee loops/$ARM.done
