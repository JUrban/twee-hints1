#!/bin/bash
# (23 Nov) PLN1 (notes/2026-11-23-conditional.md, "Plain runs"): every goal not in the 21:39 trusted list, one plain
# 5 s twee run (no rule model, no hints, no PG) with only trusted siblings, 30 earlier and 10 later, and 100 kNN
# trusted lemmas (exp/condprove.py --proved). Every proof is a real one. 4 threads; cond/PLN1 (outside loops/).
cd /project/hintwork
[ -e cond/PLN1 ] && { echo "cond/PLN1 exists"; exit 1; }
echo "PLN1 start $(date '+%d %T')" > cond/PLN1.pids
python3 -u /project/twee/hints/exp/condprove.py cond/PLN1 -j 4 --time 5 --sibs 30 --after 10 --knn 100 --proved > cond/PLN1.log 2>&1
echo "PLN1 done $(date '+%d %T') exit $?" >> cond/PLN1.pids
