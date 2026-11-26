#!/bin/bash
# (26 Nov 15:06, exp94) plainlive8: plainlive7 with condprove.py --equation in N, H and W: a conditional goal whose
# hypothesis has a variable side (t = X, X not in t) runs as its equivalent equation C[X := t] (hintsel.listen_equation).
# exp94 (the 134 unsolved such goals, same trusted set): 5 s original 0, equation 1; 60 s original 0, equation 2; the
# original only 0; both imported and trusted (t1318, t1504). condimport.py reruns p/<goal>.p, so a proof is of the
# equation. Launch: PREV_N=... PREV_H=... PREV_W=... bash abs/plainlive8.sh.
# (26 Nov 00:58, exp92) plainlive7: plainlive6 with condprove.py --listen ${LISTEN:-300} in N, H and W: each run also listens
# to up to 300 unsolved plain goals of its original (twee-e61m: the search is the same); a listened goal proved there
# gets a run of the run's problem with its own conjecture, and that row goes through condimport.py as any other
# (test: scratchpad cp92, trusted without nil3_26 goals 5-10, runs of 5 and 6: 4 listened rows, condimport 6 of 6).
# Launch: PREV_N=... PREV_H=... PREV_W=... bash abs/plainlive7.sh.
# (24 Nov, notes/2026-11-23-tail-allocation.md "plainlive6") plainlive5 plus W: the local heads (unsolved goals whose
# previous goal is proved, exp/heads.py --local) other than the first heads, at H's setting (100+30 siblings, 400 kNN,
# 60 s), rerun only when a goal's axioms or sibling lemmas changed (condprove.py --prev-ignore-knn): a newly proved
# sibling, not a moved kNN list (with kNN changes nearly every local head changes every cycle, about 15-20 CPU h).
# Why: the HLW1 sweep (exp72) proved 4 new local heads in its first 123 runs (1.32 per CPU h) while production made 0 in
# 1,000 runs. W's first --prev is cond/HLW1 (PREV_W), so HLW1's failures are not rerun. N and H as plainlive5:
#   N: 30 earlier and 10 later siblings, 100 kNN, 5 s, every changed problem
#   H: the first heads, 100+30 siblings, 400 kNN, 60 s, every changed problem (kNN changes included)
# each with its own --prev chain (cond/PLNL/c<k><S>), the context loops/UL/solved.tsv at the cycle's start, plain,
# ${J:-3} threads; proofs into loops/CI2 and loops/UL. A cycle starts at most every ${EVERY:-1800} s. Stops after a
# cycle when cond/PLNL.stop exists. PREV_N, PREV_H, PREV_W: the first cycle's --prev dirs.
cd /project/hintwork
L_="--listen ${LISTEN:-300} --equation"
declare -A ARGS=([N]="--time 5 --sibs 30 --after 10 --knn 100 $L_" [H]="--time 60 --sibs 100 --after 30 --knn 400 $L_"
                 [W]="--time 60 --sibs 100 --after 30 --knn 400 --prev-ignore-knn $L_")
declare -A TM=([N]=5 [H]=60 [W]=60)
declare -A PREV=([N]=${PREV_N:?} [H]=${PREV_H:?} [W]=${PREV_W:?})
k=$(ls -d cond/PLNL/c* 2>/dev/null | sed 's/.*\/c//; s/[A-Z.].*//' | sort -n | tail -1); k=${k:-0}
echo "plainlive8 start $(date '+%d %T') pid $$ prev N ${PREV[N]} H ${PREV[H]} W ${PREV[W]}" >> cond/PLNL/log
while [ ! -e cond/PLNL.stop ]; do
  k=$((k+1)); t0=$(date +%s)
  cut -f1 loops/UL/solved.tsv | sort -u > cond/PLNL/c$k.trusted
  python3 /project/twee/hints/exp/heads.py cond/PLNL/c$k.trusted > cond/PLNL/c$k.heads
  python3 /project/twee/hints/exp/heads.py cond/PLNL/c$k.trusted --local | grep -v -x -F -f cond/PLNL/c$k.heads > cond/PLNL/c$k.lheads
  for S in N H W; do
    C=cond/PLNL/c$k$S
    O=""; [ $S = H ] && O="--only cond/PLNL/c$k.heads"; [ $S = W ] && O="--only cond/PLNL/c$k.lheads"
    python3 -u /project/twee/hints/exp/condprove.py $C --trusted cond/PLNL/c$k.trusted --prev ${PREV[$S]} -j ${J:-3} \
      ${ARGS[$S]} $O --proved > $C.log 2>&1
    python3 /project/twee/hints/exp/condimport.py $C loops/CI2 --trusted cond/PLNL/c$k.trusted --time ${TM[$S]} > $C.import 2>&1
    flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI2 > $C.merge 2>&1
    echo "c$k$S $(date '+%d %T') ran $(grep -c -P '\t(THM|NO|TIMEOUT)\t' $C/results.tsv) THM $(grep -c -P '\tTHM\t' $C/results.tsv) $(tail -1 $C.import) | $(tail -1 $C.merge)" >> cond/PLNL/log
    PREV[$S]=$C
  done
  while [ $(( $(date +%s) - t0 )) -lt ${EVERY:-1800} ] && [ ! -e cond/PLNL.stop ]; do sleep 30; done
done
echo "plainlive8 stop $(date '+%d %T')" >> cond/PLNL/log
