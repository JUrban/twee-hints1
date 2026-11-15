#!/bin/bash
# Unfolded runs with 6 vs 12 sibling lemmas (15 Nov 13:55; Prover9's proofs had 12): sets/p9no_v from ULsV, fresh 20 s.
cd /project/hintwork
run() { D=$1; L=$2
python3 -u /project/twee/hints/loop.py sets/p9no_v loops/$D --init loops/ULsV --start 1 --rounds 1 --keep-out -j 2 \
  --pool original --wall-factor 15 --unfold \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas $L --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/36 $(date +%T)" | tee loops/$D.done; }
run UFL6 6 &
run UFL12 12 &
wait
