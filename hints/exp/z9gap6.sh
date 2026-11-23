#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "At 100 lemmas") The pre-check at 200 and 400 kNN lemmas on the 235 half2
# goals: similarity (cond/ZK2S, cond/ZK4S) against lr2h (cond/ZK2H, cond/ZK4H; pool 1,000 for 200, 2,000 for 400), the
# Z9 loop's context, 1 thread each, 4 at once. Is the ranked list a portfolio member next to a similarity one, and
# what does a second similarity size add (the control)?
cd /project/hintwork
for d in ZK2S ZK2H ZK4S ZK4H; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 -j 1 --time 5"
L="--index learned:/project/hintwork/models/lemmarank/lr2h --rank-loop /project/hintwork/loops/Z9"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK2S $C --knn 200 > cond/ZK2S.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK2H $C --knn 200 $L --rank-pool 1000 > cond/ZK2H.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK4S $C --knn 400 > cond/ZK4S.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK4H $C --knn 400 $L --rank-pool 2000 > cond/ZK4H.log 2>&1 &
wait
echo "z9gap6 done $(date '+%d %T')" >> cond/ZK4H.log
