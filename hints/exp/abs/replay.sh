#!/bin/bash
# From-scratch replay on unseen originals (16 Nov 12:05): the 3 holdout originals a_of_aa, lra2aa,
# nil3_23_32_to_26 (sets/rp3, 1,320 goals; production has 1,109 of them after 3 days) with their proofs removed
# (loops/RPs = UL at 12:00 minus them). The final pipeline runs them as on a new benchmark part:
# production's cascade settings (abs/ul34.sh) without the learned scheduler, which was trained on production's
# history of these goals. Context: the other originals' proofs as kNN lemma sources. 4 workers. --sync 60 takes in
# the proofs of abs/rpx.sh (live proof-step transfer beside it, 12:20).
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/rp3 loops/${ARM:-RP} --init loops/RPs --start 1 --cascade 5,80,320 --cascade-start -1 --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j ${J:-4} --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,80 --retry-hints 1.25 --fresh-first --far-retry --retry-knn --sync 60 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/${ARM:-RP}.log 2>&1
echo "${ARM:-RP}: $(tail -1 loops/${ARM:-RP}.log) $(date +%T)" | tee loops/${ARM:-RP}.done
