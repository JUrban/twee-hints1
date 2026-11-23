#!/bin/bash
# (23 Nov, notes/2026-11-23-plain-sizes.md "Pre-check with siblings") exp/z9gap5-8.sh had no sibling lemmas (--set
# sets/z9gap500 made the sibling pool the 500 unproved gap goals). Here --set sets/all: the 235 half2 gap goals in Z9's
# context with proved siblings, the plain levels' settings (condprove's earlier+later siblings for loop.py's sM either
# side): P4B's plk100s40 (cond/ZQA1: 30+10 siblings, 100 kNN) and plk400s130 (ZQA2: 100+30, 400) against Q5B's
# plk400s40 (ZQB1: 30+10, 400) and plk1600s130 (ZQB2: 100+30, 1,600). 1 thread each, 4 at once.
cd /project/hintwork
for d in ZQA1 ZQA2 ZQB1 ZQB2; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/all --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved -j 1 --time 5"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZQA1 $C --sibs 30 --after 10 --knn 100 > cond/ZQA1.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZQA2 $C --sibs 100 --after 30 --knn 400 > cond/ZQA2.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZQB1 $C --sibs 30 --after 10 --knn 400 > cond/ZQB1.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZQB2 $C --sibs 100 --after 30 --knn 1600 > cond/ZQB2.log 2>&1 &
wait
echo "z9gap9 done $(date '+%d %T')" >> cond/ZQB2.log
