#!/bin/bash
# (13:00) ARM=RPc: beside the clean replay.
# Live proof-step transfer for the replay (16 Nov 12:15): as abs/xfrlive.sh, beside loops/RP, candidates only from
# sets/rp3, every 10 minutes, 30 kNN lemmas as the replay.
cd /project/hintwork
python3 /project/twee/hints/transfer.py live loops/${ARM:-RP} loops/${ARM:-RP}X -j ${J:-2} --time 20 --src-lemmas 6 --every 600 --set /project/hintwork/sets/rp3 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/${ARM:-RP}X.log 2>&1
