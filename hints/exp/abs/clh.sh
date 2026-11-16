#!/bin/bash
# Long climbs on the stuck heads (16 Nov 04:20). sets/heads_stuck = the 111 heads (each original's first unsolved
# goal); every one failed a short live climb (5 s sketches, 20 s final). Here: the live climber's config (FUD + one
# more axiom up steps + 2 random theory slots) with a 160 abstract s final run and 24 sketch runs, from snapshot ULsY
# (UL at 04:15), 4 workers, --chain. Baseline: a second short climb in an unchanged context, 2 proofs in 87 (2ak).
# Proofs go into UL with merge.py.
cd /project/hintwork
L="--init loops/ULsY --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
C="--m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time ${FINAL:-160}"
python3 /project/twee/hints/climb.py sets/${SET:-heads_stuck} loops/${ARM:-CLH} $C -j ${J:-4} -- $L \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/${ARM:-CLH}.log 2>&1
echo "${ARM:-CLH} $(tail -1 loops/${ARM:-CLH}.log) $(date +%T)" | tee loops/${ARM:-CLH}.done
