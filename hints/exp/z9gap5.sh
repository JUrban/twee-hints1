#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "Z9's gap") The pre-check at 100 kNN lemmas (the kN members' size) on the
# 235 half2 goals: cond/ZKS similarity, cond/ZKH lr2h (pool 1,000), 1 thread each at once; started after abs/z9gap3.sh
# and abs/z9gap4.sh (the half1 arms) end.
cd /project/hintwork
until grep -q "z9gap3 done" cond/ZGH1.log 2>/dev/null && grep -q "z9gap4 done" cond/ZGM1.log 2>/dev/null; do sleep 20; done
for d in ZKS ZKH; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 --knn 100 -j 1 --time 5"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZKS $C > cond/ZKS.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZKH $C --index learned:/project/hintwork/models/lemmarank/lr2h \
  --rank-loop /project/hintwork/loops/Z9 --rank-pool 1000 > cond/ZKH.log 2>&1 &
wait
echo "z9gap5 done $(date '+%d %T')" >> cond/ZKH.log
