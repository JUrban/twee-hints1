#!/bin/bash
# (23 Nov) abs/plainlive2.sh with the ranked setting L in place of W (notes/2026-11-23-lemma-ranker.md, "Live loop"):
#   N: 30 earlier and 10 later siblings, 100 kNN (PLN1, PLN2, plainlive.sh)
#   L: 100 earlier and 30 later siblings, 400 kNN ranked by models/lemmarank/lr1 (PLL1; numpy, the system python)
# each with its own --prev chain (cond/PLNL/c<k><S>), the context loops/UL/solved.tsv at the cycle's start, plain 5 s,
# ${J:-3} threads; proofs into loops/CI2 and loops/UL. A cycle starts at most every ${EVERY:-1800} s. Stops after a
# cycle when cond/PLNL.stop exists. PREV_N, PREV_L: the first cycle's --prev dirs.
cd /project/hintwork
declare -A ARGS=([N]="--sibs 30 --after 10 --knn 100" [L]="--sibs 100 --after 30 --knn 400 --index learned:/project/hintwork/models/lemmarank/${MODEL:-lr1}")
declare -A PREV=([N]=${PREV_N:?} [L]=${PREV_L:?})
k=$(ls -d cond/PLNL/c* 2>/dev/null | sed 's/.*\/c//; s/[A-Z.].*//' | sort -n | tail -1); k=${k:-0}
echo "plainlive3 start $(date '+%d %T') pid $$ prev N ${PREV[N]} L ${PREV[L]}" >> cond/PLNL/log
while [ ! -e cond/PLNL.stop ]; do
  k=$((k+1)); t0=$(date +%s)
  cut -f1 loops/UL/solved.tsv | sort -u > cond/PLNL/c$k.trusted
  for S in N L; do
    C=cond/PLNL/c$k$S
    python3 -u /project/twee/hints/exp/condprove.py $C --trusted cond/PLNL/c$k.trusted --prev ${PREV[$S]} -j ${J:-3} --time 5 \
      ${ARGS[$S]} --proved > $C.log 2>&1
    python3 /project/twee/hints/exp/condimport.py $C loops/CI2 --trusted cond/PLNL/c$k.trusted > $C.import 2>&1
    flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI2 > $C.merge 2>&1
    echo "c$k$S $(date '+%d %T') ran $(grep -c -P '\t(THM|NO|TIMEOUT)\t' $C/results.tsv) THM $(grep -c -P '\tTHM\t' $C/results.tsv) $(tail -1 $C.import) | $(tail -1 $C.merge)" >> cond/PLNL/log
    PREV[$S]=$C
  done
  while [ $(( $(date +%s) - t0 )) -lt ${EVERY:-1800} ] && [ ! -e cond/PLNL.stop ]; do sleep 30; done
done
echo "plainlive3 stop $(date '+%d %T')" >> cond/PLNL/log
