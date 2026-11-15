#!/bin/bash
# v2.sh VARIANT...: harder long eval on sets/v2_hard (8 fam_long failures + next 30 unsolved goals of
# aK2_eq_aK3_d and nil3_30), 300 abstract s, rm4t + lemmas 3 + 10 subset-kNN, outputs kept for stallsim
cd /project/hintwork
V="python3 /project/twee/hints/loop.py sets/v2_hard"
C="--init loops/V2base --start 1 --rounds 1 --timeout 300 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e18 --keep-out -j 9"
A="--abstract-time 2000 --max-cpu 1200"
for v in "$@"; do
  case $v in
    p) $V loops/V2p $C --pool original --args="$A" > loops/V2p.log 2>&1 ;;
    k) $V loops/V2k $C --pool knn:30:200 --args="$A" > loops/V2k.log 2>&1 ;;
    n) $V loops/V2n $C --pool original --max-hints 0 --rerun-unhinted --args="$A" > loops/V2n.log 2>&1 ;;
  esac
  echo "V2$v: $(tail -1 loops/V2$v.log)"
done
