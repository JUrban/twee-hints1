#!/bin/bash
# (23 Nov) COND1's one unconditional proof (nil3_30__goal_473) again through loop.py, so that it has a loop record:
# production's context (--init loops/UL), 10 sibling lemmas, 30 kNN lemmas (subsets), plain twee (TWEE_PG_ARGS unset),
# no rule model, 5 s; loops/CU1. If proved: trust.py, then merge.py into loops/UL.
cd /project/hintwork
[ -e loops/CU1 ] && { echo "loops/CU1 exists"; exit 1; }
unset TWEE_PG_ARGS
python3 -u /project/twee/hints/loop.py sets/condu1 loops/CU1 --init loops/UL --start 1 --rounds 1 --keep-out -j 1 \
  --lemmas 10 --lemma-knn 30 --lemma-subsets --twee /project/bin/twee-pg61 --timeout 5 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/CU1.log 2>&1
echo "CU1 exit $?"
