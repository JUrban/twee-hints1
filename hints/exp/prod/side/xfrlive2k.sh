#!/bin/bash
# (20 Nov 10:35) gmlive2.sh / xfrlive2.sh with --keep-out: kept outputs (USEDAXIOMS) are the lemma records exp/trust.py needs (notes/2026-11-20-p9-negation-bug.md)
# (16 Nov 17:15) every 5 minutes and 30 kNN lemmas, as production (2am) and the from-scratch result (2aq: a faster
# cycle passes reuse on sooner).
# Live proof-step transfer beside production (16 Nov 05:45; transfer.py live, REPORT 2al): every 20 minutes, the
# unsolved goals that are steps of UL's proofs from the same or weaker axioms, or instances of its proven goals of
# other originals, not tried with the same first source, get one fresh 20 abstract s run with the source proofs'
# steps as hints and the source goals (and their 5 nearest proven goals below) as lemmas; proofs go into UL.
cd /project/hintwork
python3 /project/twee/hints/transfer.py live loops/UL loops/XFL -j ${J:-2} --time 20 --src-lemmas 6 --every 300 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 --keep-out \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/XFL.log 2>&1
