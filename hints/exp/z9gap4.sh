#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "Z9's gap") A mixed arm of the Z9-gap pre-check: the similarity list's
# top 15, then the held-out ranker's best 15 of the rest of its top 1,000 (condprove.py --rank-mix 15): cond/ZGM2 (the
# half2 goals, lr2h), then cond/ZGM1 (the half1 goals, lr2h1); 1 thread.
cd /project/hintwork
for d in ZGM2 ZGM1; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 --knn 30 -j 1 --time 5 --rank-loop /project/hintwork/loops/Z9 --rank-pool 1000 --rank-mix 15"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGM2 $C --only sets/z9gap500h2 --index learned:/project/hintwork/models/lemmarank/lr2h > cond/ZGM2.log 2>&1
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGM1 $C --only sets/z9gap500h1 --index learned:/project/hintwork/models/lemmarank/lr2h1 > cond/ZGM1.log 2>&1
echo "z9gap4 done $(date '+%d %T')" >> cond/ZGM1.log
