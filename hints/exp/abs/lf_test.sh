#!/bin/bash
# Folded lemma instances (15 Nov 11:40): production context + --lemma-fold 8, fresh 20 s, folded twee.
# LF_p9: the 9 Prover9 proofs (snapshot ULsP; folded 2, unfolded 7). LF_fr: sets/lf116 = p9no40 + unf80 from ULsU
# (all stalled in production; unfolded: 3 of the first 10 p9no40, 1 of 28 unf80).
cd /project/hintwork
run() { D=$1; S=$2; N=$3; J=$4
python3 -u /project/twee/hints/loop.py sets/$N loops/$D --init loops/$S --start 1 --rounds 1 --keep-out -j $J \
  --pool original --wall-factor 15 --lemma-fold 8 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/$N) $(date +%T)" | tee loops/$D.done; }
run LF_p9 ULsP p9l9 1 &
run LF_fr ULsU lf116 3 &
wait
