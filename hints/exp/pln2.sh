#!/bin/bash
# (23 Nov) PLN2: PLN1's plain sweep again in the context of trusted list t0641 (48,466: production's own new proofs and
# PLN1's 22 merged), --prev cond/PLN1: only goals whose problem text changed are run. 3 threads; cond/PLN2.
cd /project/hintwork
[ -e cond/PLN2 ] && { echo "cond/PLN2 exists"; exit 1; }
echo "PLN2 start $(date '+%d %T')" > cond/PLN2.pids
python3 -u /project/twee/hints/exp/condprove.py cond/PLN2 --trusted loops/TRUSTNOW/t0641.trusted --prev cond/PLN1 -j 3 --time 5 \
  --sibs 30 --after 10 --knn 100 --proved > cond/PLN2.log 2>&1
echo "PLN2 done $(date '+%d %T') exit $?" >> cond/PLN2.pids
