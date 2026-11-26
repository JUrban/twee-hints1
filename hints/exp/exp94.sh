#!/bin/bash
# (26 Nov, exp94) the unsolved conditional goals with a variable-side hypothesis (exp/sets/exp94.goals), as their
# original problem (arm O) and as the equivalent equation (arm E, condprove.py --equation), the same trusted set
# (exp/sets/exp94.trusted), plainlive's N setting (5 s) then its H setting (60 s), no listening; twee-pg61, abstract time.
# Run from /project/hintwork: bash /project/twee/hints/exp/exp94.sh OUTDIR
D=${1:?}; mkdir -p $D
S=/project/twee/hints/exp/sets
for st in N H; do
  [ $st = N ] && A="--time 5 --sibs 30 --after 10 --knn 100" || A="--time 60 --sibs 100 --after 30 --knn 400"
  for arm in O E; do
    X=""; [ $arm = E ] && X="--equation"
    echo "$st$arm start $(date '+%d %T')" >> $D/log
    python3 -u /project/twee/hints/exp/condprove.py $D/$st$arm --trusted $S/exp94.trusted --only $S/exp94.goals \
      -j ${J:-4} $A $X --proved > $D/$st$arm.log 2>&1
    echo "$st$arm end $(date '+%d %T') THM $(grep -c -P '\tTHM\t' $D/$st$arm/results.tsv)" >> $D/log
  done
done
