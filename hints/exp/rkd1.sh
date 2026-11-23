#!/bin/bash
# (23 Nov) RKD1: training data for a learned lemma ranker (notes/2026-11-23-lemma-ranker.md): plain runs of 800 solved
# goals near the frontier (sets/rank800: the later half of the trusted goals of the 40 originals with the most
# unsolved goals, seed 65) with 200+60 trusted siblings and 1,000 kNN lemmas (the goal itself excluded), 5 s,
# 2 threads, the context t0641. Real proofs of solved goals: kept in cond/RKD1, never imported.
cd /project/hintwork
[ -e cond/RKD1 ] && { echo "cond/RKD1 exists"; exit 1; }
echo "RKD1 start $(date '+%d %T')" > cond/RKD1.pids
python3 -u /project/twee/hints/exp/condprove.py cond/RKD1 --trusted loops/TRUSTNOW/t0641.trusted --only sets/rank800 --all \
  -j 2 --time 5 --sibs 200 --after 60 --knn 1000 --proved > cond/RKD1.log 2>&1
echo "RKD1 done $(date '+%d %T') exit $?" >> cond/RKD1.pids
