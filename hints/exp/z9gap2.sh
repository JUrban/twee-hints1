#!/bin/bash
# (23 Nov, notes/2026-11-23-lemma-ranker.md "Z9's gap") abs/z9gap.sh's ranked arm again with lr2h (models/lemmarank/lr2h:
# LR2.pkl without half2's originals) on the 235 goals of sets/z9gap500 in half2 (sets/z9gap500h2): lr2 had been
# trained on 25 of the 500 and on goals of 403's originals. cond/ZGH, 1 thread; compared with cond/ZGS on those 235.
cd /project/hintwork
[ -e cond/ZGH ] && { echo "cond/ZGH exists"; exit 1; }
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGH --set sets/z9gap500 --only sets/z9gap500h2 --trusted cond/Z9.trusted \
  --proved --sibs 4 --after 2 --knn 30 -j 1 --time 5 --index learned:/project/hintwork/models/lemmarank/lr2h \
  --rank-loop /project/hintwork/loops/Z9 --rank-pool 1000 > cond/ZGH.log 2>&1
echo "z9gap2 done $(date '+%d %T')" >> cond/ZGH.log
