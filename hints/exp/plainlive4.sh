#!/bin/bash
# (23 Nov, notes/2026-11-23-plain-sizes.md "The frontier is 92 heads") abs/plainlive3.sh plus a heads setting H:
#   N: 30 earlier and 10 later siblings, 100 kNN, 5 s
#   L: 100 earlier and 30 later siblings, 400 kNN ranked by models/lemmarank/${MODEL:-lr2}, 5 s
#   H: the cycle's heads only (each original's first unsolved goal in the cycle's context), 100+30 siblings, 400 kNN
#      by similarity, 60 s (HDW1's setting; 2 of its first 22 heads were proved at 13-15 s)
# each with its own --prev chain (cond/PLNL/c<k><S>), the context loops/UL/solved.tsv at the cycle's start, plain,
# ${J:-3} threads; proofs into loops/CI2 and loops/UL (condimport.py at the setting's time). A cycle starts at most
# every ${EVERY:-1800} s. Stops after a cycle when cond/PLNL.stop exists. PREV_N, PREV_L, PREV_H: the first cycle's
# --prev dirs.
cd /project/hintwork
declare -A ARGS=([N]="--time 5 --sibs 30 --after 10 --knn 100" [L]="--time 5 --sibs 100 --after 30 --knn 400 --index learned:/project/hintwork/models/lemmarank/${MODEL:-lr2}" [H]="--time 60 --sibs 100 --after 30 --knn 400")
declare -A TM=([N]=5 [L]=5 [H]=60)
declare -A PREV=([N]=${PREV_N:?} [L]=${PREV_L:?} [H]=${PREV_H:?})
k=$(ls -d cond/PLNL/c* 2>/dev/null | sed 's/.*\/c//; s/[A-Z.].*//' | sort -n | tail -1); k=${k:-0}
echo "plainlive4 start $(date '+%d %T') pid $$ prev N ${PREV[N]} L ${PREV[L]} H ${PREV[H]}" >> cond/PLNL/log
while [ ! -e cond/PLNL.stop ]; do
  k=$((k+1)); t0=$(date +%s)
  cut -f1 loops/UL/solved.tsv | sort -u > cond/PLNL/c$k.trusted
  python3 /project/twee/hints/exp/heads.py cond/PLNL/c$k.trusted > cond/PLNL/c$k.heads
  for S in N L H; do
    C=cond/PLNL/c$k$S
    O=""; [ $S = H ] && O="--only cond/PLNL/c$k.heads"
    python3 -u /project/twee/hints/exp/condprove.py $C --trusted cond/PLNL/c$k.trusted --prev ${PREV[$S]} -j ${J:-3} \
      ${ARGS[$S]} $O --proved > $C.log 2>&1
    python3 /project/twee/hints/exp/condimport.py $C loops/CI2 --trusted cond/PLNL/c$k.trusted --time ${TM[$S]} > $C.import 2>&1
    flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI2 > $C.merge 2>&1
    echo "c$k$S $(date '+%d %T') ran $(grep -c -P '\t(THM|NO|TIMEOUT)\t' $C/results.tsv) THM $(grep -c -P '\tTHM\t' $C/results.tsv) $(tail -1 $C.import) | $(tail -1 $C.merge)" >> cond/PLNL/log
    PREV[$S]=$C
  done
  while [ $(( $(date +%s) - t0 )) -lt ${EVERY:-1800} ] && [ ! -e cond/PLNL.stop ]; do sleep 30; done
done
echo "plainlive4 stop $(date '+%d %T')" >> cond/PLNL/log
