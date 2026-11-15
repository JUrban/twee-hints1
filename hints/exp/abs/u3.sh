#!/bin/bash
# u3.sh VARIANT...: all unsolved goals (after ALL_lem r2 + G1) of R1dist_to_aa1, aK2_eq_aK3_a, nil3_31 (sets/u3),
# 20 abstract s, rm4t + lemmas 3 + 10 subset-kNN, e19; online vs offline pools
cd /project/hintwork
V="python3 /project/twee/hints/loop.py sets/u3"
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e19 --keep-out -j ${J:-5}"
A="--abstract-time 2000 --max-cpu 200"
for v in "$@"; do
  case $v in
    k)  $V loops/U3$v $C --pool knn:30:100 --args="$A" ;;
    ko) $V loops/U3$v $C --pool knn:30:100 --online --args="$A" ;;
    p)  $V loops/U3$v $C --pool original --args="$A" ;;
    po) $V loops/U3$v $C --pool original --online --args="$A" ;;
  esac > loops/U3$v.log 2>&1
  echo "U3$v: $(tail -1 loops/U3$v.log) $(date +%T)" | tee loops/U3$v.done
done
