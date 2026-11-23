#!/bin/bash
# (23 Nov) exp/condprove.py on every goal not in the 22 Nov 21:39 trusted list: its 10 nearest earlier siblings
# assumed (proved or not) plus 30 kNN trusted lemmas, one plain 5 s twee-pg61 run, 6 threads. OUT is outside loops/.
cd /project/hintwork
[ -e cond/COND1 ] && { echo "cond/COND1 exists"; exit 1; }
echo "COND1 start $(date '+%d %T')" > cond/COND1.pids
python3 -u /project/twee/hints/exp/condprove.py cond/COND1 -j 6 --time 5 --sibs 10 --knn 30 > cond/COND1.log 2>&1
echo "COND1 done $(date '+%d %T') exit $?" >> cond/COND1.pids
