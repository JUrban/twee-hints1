#!/bin/bash
# (19 Nov 16:53) exp34: the climber's conditional proofs (notes/2026-11-19-climber-outputs.md): unsolved targets whose
# sketch proof used only sibling assumptions, all proven by production since. Arms A plain, B + the siblings as lemmas,
# C + the sketch steps as hints; 20 s each, the climber's production context (abs/clhl2.sh's loop options).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
python3 -u /project/twee/hints/exp/condtest.py loops/UL loops/CT1 --budget ${T:-20} -j ${J:-2} -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CT1.log 2>&1
echo "CT1 $(date +%T)" > loops/CT1.done
