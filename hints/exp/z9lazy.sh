#!/bin/bash
# (23 Nov, notes/2026-11-23-plain-sizes.md "Lazy lemma axioms") twee-e63 --lazy-lemmas on the 235 half2 gap goals with
# ZKGS's settings (1,600 similarity kNN lemmas, no siblings, plain 5 s, Z9's context): cond/ZLG1 factor 1, cond/ZLG5
# factor 0.5, against cond/ZKGS (twee-pg61, eager: 40 proofs). 1 thread each.
cd /project/hintwork
for d in ZLG1 ZLG5; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 --knn 1600 -j 1 --time 5 --twee /project/bin/twee-e63"
nice -n 15 python3 -u /project/twee/hints/exp/condprove.py cond/ZLG1 $C --args "--lazy-lemmas" > cond/ZLG1.log 2>&1 &
nice -n 15 python3 -u /project/twee/hints/exp/condprove.py cond/ZLG5 $C --args "--lazy-lemmas --lazy-lemma-factor 0.5" > cond/ZLG5.log 2>&1 &
wait
echo "z9lazy done $(date '+%d %T')" >> cond/ZLG5.log
