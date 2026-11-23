#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "The other half and 100 lemmas") The merged lists: similarity's top N, then
# lr2h's best N of the rest (Ranker.MIX, condprove.py --rank-mix N), at 200 (N 100, pool 1,000; cond/ZK2M) and 400
# (N 200, pool 2,000; cond/ZK4M) kNN lemmas on the 235 half2 goals, Z9's context. Proofs of these goals use up to 20
# kNN lemmas spread over ranks 0-100, so a list must hold the whole set: does a merged list hold both arms' sets?
# Started after abs/z9gap6.sh ends.
cd /project/hintwork
until grep -q "z9gap6 done" cond/ZK4H.log 2>/dev/null; do sleep 20; done
for d in ZK2M ZK4M; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 -j 1 --time 5"
L="--index learned:/project/hintwork/models/lemmarank/lr2h --rank-loop /project/hintwork/loops/Z9"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK2M $C --knn 200 $L --rank-pool 1000 --rank-mix 100 > cond/ZK2M.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK4M $C --knn 400 $L --rank-pool 2000 --rank-mix 200 > cond/ZK4M.log 2>&1 &
wait
echo "z9gap7 done $(date '+%d %T')" >> cond/ZK4M.log
