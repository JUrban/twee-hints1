#!/bin/bash
# Portfolio probe (15 Nov): fresh 20 s runs of the stalled goals (abs/stalled_set.py) in a variant
# of the L0 configuration, from snapshot loops/ULsM (solved.tsv + hints of UL after A/B 2).
# A rerun in an unchanged context with the same settings repeats a deterministic search;
# which variants prove goals that the base fails, and what does their union give?
#   V=name J=workers bash abs/port.sh SET
cd /project/hintwork
SET=$1
C="--init loops/ULsM --start 1 --rounds 1 --keep-out -j ${J:-2} --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22"
X=()
case "$V" in
  base) ;;
  ord1) X=(--p9-orders 4 --p9-order-offset 1) ;;
  ord2) X=(--p9-orders 4 --p9-order-offset 2) ;;
  nomodel) M="" ;;
  lem12) L="${L/--lemmas 6/--lemmas 12}" ;;
  lem2) L="${L/--lemmas 6/--lemmas 2}" ;;
  hint500) X=(--max-hints 500) ;;
  thr) X=("--model-args=--rule-threshold 0.3 --rule-penalty 5") ;;
  tier) C="${C/--pool original/--pool tier:20:500:0.1}" ;;
  knn) C="${C/--pool original/--pool knn:20:1000}" ;;
  rm7t) M="${M//rm4t/rm7t}" ;;
  *) echo "unknown V=$V"; exit 1 ;;
esac
python3 -u /project/twee/hints/loop.py $SET loops/PO_$V${T:+_$T} $C $M $L "${X[@]}" --timeout ${T:-20} \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/PO_$V${T:+_$T}.log 2>&1
echo "PO_$V $(grep -c THM loops/PO_$V${T:+_$T}/r1/results.tsv)/$(wc -l < $SET) $(date +%T)" | tee loops/PO_$V${T:+_$T}.done
