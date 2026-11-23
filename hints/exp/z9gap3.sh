#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "Z9's gap") The other half of the Z9-gap pre-check: the goals of
# sets/z9gap500 in half1 (sets/z9gap500h1) with lr2h1 (LR2.pkl without half1's originals), as abs/z9gap2.sh;
# cond/ZGH1, 1 thread. With cond/ZGH every one of the 500 has a ranker that has not seen its original.
cd /project/hintwork
[ -e cond/ZGH1 ] && { echo "cond/ZGH1 exists"; exit 1; }
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGH1 --set sets/z9gap500 --only sets/z9gap500h1 --trusted cond/Z9.trusted \
  --proved --sibs 4 --after 2 --knn 30 -j 1 --time 5 --index learned:/project/hintwork/models/lemmarank/lr2h1 \
  --rank-loop /project/hintwork/loops/Z9 --rank-pool 1000 > cond/ZGH1.log 2>&1
echo "z9gap3 done $(date '+%d %T')" >> cond/ZGH1.log
