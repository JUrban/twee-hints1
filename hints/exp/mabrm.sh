#!/bin/bash
# (19 Nov 19:52) exp37's paired online test of the retrained rule models (notes/2026-11-19-retrained-models.md):
# abs/mabpg.sh (exp33) on the 400 newest production proofs (sets/ul400n, held out of every model's training) from
# their snapshot loops/ULsN19 (production's solved rows before the first of them). Fresh 20 s, PG 0.25, twee-pg61,
# 6 sibling and 10 kNN lemmas; only the model differs. Control M=rm4t.
#   M=rm9a T=20 J=1 bash abs/mabrm.sh   -> loops/MR_<M>_<T>
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=MR_${M}_${T:-20}
python3 -u /project/twee/hints/loop.py sets/ul400n loops/$D --init loops/ULsN19 --start 1 --rounds 1 --keep-out -j ${J:-1} \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/$M.bin,/project/hintwork/models/$M.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout ${T:-20} \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/ul400n) $(date +%T)" | tee loops/$D.done
