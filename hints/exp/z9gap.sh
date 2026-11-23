#!/bin/bash
# (23 Nov 13:20, notes/2026-11-23-lemma-ranker.md "Z9's gap") Offline pre-check for exp65: 500 goals production solved
# and Z9 (8 hours from zero) did not (sets/z9gap500, seed 66), in Z9's final context (cond/Z9.trusted: loops/Z9/solved.tsv),
# plain 5 s twee (condprove.py --proved: Z9-proved siblings only, 4 earlier + 2 later, 30 kNN lemmas), two arms at
# once, 1 thread each:
#   cond/ZGS: the similarity list (LemmaIndex, subsets);
#   cond/ZGR: lr2's order of the similarity list's top 1,000 (loop.py --lemma-ranker-all's pool), its use counts,
#             proof steps and sibling features from loops/Z9 (--rank-loop), not production's.
cd /project/hintwork
for d in ZGS ZGR; do [ -e cond/$d ] && { echo "cond/$d exists"; exit 1; }; done
C="--set sets/z9gap500 --trusted cond/Z9.trusted --proved --sibs 4 --after 2 --knn 30 -j 1 --time 5"
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGS $C > cond/ZGS.log 2>&1 &
nice -n 10 python3 -u /project/twee/hints/exp/condprove.py cond/ZGR $C --index learned:/project/hintwork/models/lemmarank/lr2 \
  --rank-loop /project/hintwork/loops/Z9 --rank-pool 1000 > cond/ZGR.log 2>&1 &
wait
echo "z9gap done $(date '+%d %T')" >> cond/ZGR.log
