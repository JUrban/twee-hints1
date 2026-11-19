#!/bin/bash
# (19 Nov 17:45) exp36: the climbs' sketch hints, ablated on the climber's own proofs (notes/2026-11-19-climb-ablation.md;
# user 17:20: "presumably they helped inside the climb"). 55 climber proofs; per proof the pool alone (P) and the
# sketch steps saved before it plus the pool (S), at the directory's final time, context as of the proof.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
python3 -u /project/twee/hints/exp/climbablate.py loops/CA1 "$@" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CA1.log 2>&1
echo "CA1 $(date +%T)" > loops/CA1.done
