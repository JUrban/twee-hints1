#!/bin/bash
# Goals that are steps of existing proofs (16 Nov 04:45; transfer.py): each unsolved goal of sets/transfer1.tsv is a
# step (up to variable names) of a proof of another goal with the same or weaker axioms; one fresh 20 abstract s run
# with those proofs' steps first, then the usual pool and lemmas, from snapshot ULsY. Proofs -> merge.py into UL.
cd /project/hintwork
python3 /project/twee/hints/transfer.py run sets/transfer1.tsv loops/${ARM:-XFR} -j ${J:-3} --time ${T:-20} -- \
  --init loops/ULsY --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/${ARM:-XFR}.log 2>&1
echo "${ARM:-XFR} $(tail -1 loops/${ARM:-XFR}.log) $(date +%T)" | tee loops/${ARM:-XFR}.done
