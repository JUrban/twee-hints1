#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "Size, not order") Plain 5 s runs on the 235 half2 gap goals (Z9's context)
# proved 11/20/22/35 with 30/100/200/400 similarity kNN lemmas: how far does size go, and do more siblings matter?
# cond/ZK8S 800 lemmas, cond/ZKGS 1,600, cond/ZK4T 400 lemmas with 40 earlier siblings (exp64's plain levels take 40
# and 130), 1 thread each, 3 at once (abs/z9gap7.sh, the merged lists, stopped after 2 goals: the ranker is not the lever).
cd /project/hintwork
for d in ZK8S ZKGS ZK4T; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved --after 2 -j 1 --time 5"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK8S $C --sibs 4 --knn 800 > cond/ZK8S.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZKGS $C --sibs 4 --knn 1600 > cond/ZKGS.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZK4T $C --sibs 40 --knn 400 > cond/ZK4T.log 2>&1 &
wait
echo "z9gap8 done $(date '+%d %T')" >> cond/ZK4T.log
