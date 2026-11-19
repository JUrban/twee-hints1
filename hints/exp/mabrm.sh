#!/bin/bash
# (19 Nov 21:01) exp37's paired test of the retrained rule models, replayed as of each proof
# (notes/2026-11-19-retrained-models.md). Replaces the 19:52 design (one snapshot loops/ULsN19 without all 400 test
# goals): today's 400 newest proofs are sibling chains, each proved with its just-proven predecessors as lemmas, and
# without them the rm4t control proved 2 of 122. exp/modelreplay.py gives each test goal production's context as of
# its own proof (solved rows before its row), as exp36 did. Fresh 20 s, PG 0.25, twee-pg61, 6 sibling and 30 kNN
# lemmas (production's L0); only the model differs. Control M=rm4t.
#   M=rm9a T=20 bash abs/mabrm.sh   -> loops/MQ_<M>_<T>
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=MQ_${M}_${T:-20}
python3 -u /project/twee/hints/exp/modelreplay.py loops/$D sets/ul400n ${T:-20} -- --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/$M.bin,/project/hintwork/models/$M.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/results.tsv)/$(wc -l < sets/ul400n) $(date +%T)" | tee loops/$D.done
