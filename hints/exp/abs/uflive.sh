#!/bin/bash
# Unfolded-twee side worker (15 Nov 11:25): replaces the Prover9 worker (p9live.sh, stopped 10:24). Twee with the
# definitions substituted away proved 7 of Prover9's 9 proofs (folded 2) and 3 of the first 10 Prover9 failed.
# Cycles of 24 stalled goals (p9twee's targets) in loops/UFL, proofs merged into loops/UL (which --syncs them).
cd /project/hintwork
python3 -u /project/twee/hints/uflive.py loops/UL loops/UFL -j 4 --batch 24 --loop-args "--pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20" \
  --twee-args "--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/UFL.log 2>&1
