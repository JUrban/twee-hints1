#!/bin/bash
# exp28 (19 Nov 07:28): E 3.5.9 (ext/eprover a08e78c) with chain hints as a static watchlist, on exp11's 107 walls, 60 CPU s, 1 worker.
# Starts when exp23's stage3 (V100) has ended. notes/2026-11-19-eprover-watchlist.md
cd /project/hintwork/exp28
while kill -0 2580145 2>/dev/null; do sleep 60; done   # exp23 stage3.sh (V100)
E=/project/hintwork/ext/eprover/PROVER/eprover; X=/project/hintwork/exp11
mkdir -p wl out
echo "$(date +%T) start" >> run.log
for g in $(cat $X/goals107); do
  grep -q "^$g	" results.tsv 2>/dev/null && continue
  python3 mkwl.py $X/h_chain/$g.hints > wl/$g.p
  s=$(date +%s.%N)
  /usr/bin/time -f "%U %S %M" -o out/$g.time $E -s --proof-object --cpu-limit=60 -xUseWatchlist -tKBO6 \
    --static-watchlist=wl/$g.p $X/cap/tb/tmp/$g.p > out/$g.out 2> out/$g.err
  st=$(grep -m1 -o "SZS status [A-Za-z]*" out/$g.out | cut -d' ' -f3)
  echo -e "$g\t${st:-none}\t$(cat out/$g.time | tail -1 | awk '{print $1+$2"\t"$3}')" >> results.tsv
  rm -f wl/$g.p
done
echo "$(date +%T) end" >> run.log
