#!/bin/bash
# (23 Nov) The plain member as a live side loop of production (notes/2026-11-23-conditional.md, "Plain live loop"):
# each cycle takes production's solved goals (loops/UL/solved.tsv) as the trusted context, runs exp/condprove.py
# --proved on the goals not in it (30 earlier and 10 later siblings, 100 kNN lemmas, plain 5 s twee), only those
# whose problem changed since the cycle before (--prev), imports the proofs with their records into loops/CI2
# (exp/condimport.py) and merges them into loops/UL (merge.py), which the live loop's --sync takes in.
# A cycle starts at most every ${EVERY:-1800} s; 3 threads. Stops after a cycle when cond/PLNL.stop exists.
cd /project/hintwork
mkdir -p cond/PLNL
PREV=${PREV:-cond/PLN2}
k=$(ls -d cond/PLNL/c* 2>/dev/null | sed 's/.*\/c//' | sort -n | tail -1); k=${k:-0}
[ "$k" -gt 0 ] && PREV=cond/PLNL/c$k
echo "plainlive start $(date '+%d %T') pid $$ prev $PREV" >> cond/PLNL/log
while [ ! -e cond/PLNL.stop ]; do
  k=$((k+1)); C=cond/PLNL/c$k; t0=$(date +%s)
  cut -f1 loops/UL/solved.tsv | sort -u > cond/PLNL/c$k.trusted
  python3 -u /project/twee/hints/exp/condprove.py $C --trusted cond/PLNL/c$k.trusted --prev $PREV -j ${J:-3} --time 5 \
    --sibs 30 --after 10 --knn 100 --proved > $C.log 2>&1
  python3 /project/twee/hints/exp/condimport.py $C loops/CI2 --trusted cond/PLNL/c$k.trusted > $C.import 2>&1
  python3 /project/twee/hints/merge.py loops/UL loops/CI2 > $C.merge 2>&1
  echo "c$k $(date '+%d %T') ran $(grep -c -P '\t(THM|NO|TIMEOUT)\t' $C/results.tsv) THM $(grep -c -P '\tTHM\t' $C/results.tsv) $(tail -1 $C.import) | $(tail -1 $C.merge)" >> cond/PLNL/log
  PREV=$C
  while [ $(( $(date +%s) - t0 )) -lt ${EVERY:-1800} ] && [ ! -e cond/PLNL.stop ]; do sleep 30; done
done
echo "plainlive stop $(date '+%d %T')" >> cond/PLNL/log
