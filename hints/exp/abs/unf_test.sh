#!/bin/bash
# Unfolded definitions in the production context (15 Nov 10:45): frontier goals (sets/unf80: unsolved, a proven
# sibling within 3 below; production tried them folded and failed), fresh 20 s, lemmas + kNN + original pool,
# twee-e22, from snapshot ULsU (UL at 10:44). Arm U: --unfold with rm4t; arm UN: --unfold, no model.
cd /project/hintwork
run() { D=$1; shift
python3 -u /project/twee/hints/loop.py sets/unf80 loops/$D --init loops/ULsU --start 1 --rounds 1 --keep-out -j 2 \
  --pool original --wall-factor 15 "$@" \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/unf80) $(date +%T)" | tee loops/$D.done; }
run UF_U --unfold --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory &
run UF_UN --unfold &
wait
