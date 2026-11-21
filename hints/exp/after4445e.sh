#!/bin/bash
# (21 Nov 03:37) Replaces abs/after4445d.sh. When exp44/45 end (loops/exp4445.done): waits up to 20 minutes for
# loops/GO48 (written after reading the 5-hour result), then starts the half2 arms from zero, 6 workers, 5 hours,
# with LOOPARGS from loops/<ARM>.args (notes/2026-11-21-late-combo.md):
#   P2N (exp48 base): --retry-class --yield-discount 2000 --reexplore 12:0.25
#   P2O (exp48): P2N + --knn-ctx 10 --head-class
# and the step-join member (abs/stepjlive3.sh). Production stays paused (its own loop proved 2 in its last 2,000
# runs) to keep the machine near 24 CPUs. PIDs in loops/AFTERZ6.pids.
cd /project/hintwork
until [ -e loops/exp4445.done ]; do sleep 60; done
T=$(( $(date +%s) + 1200 ))
until [ -e loops/GO48 ] || [ $(date +%s) -ge $T ]; do sleep 20; done
[ -e loops/UL74.log ] && [ ! -e loops/UL74.0420.log ] && mv loops/UL74.log loops/UL74.0420.log
REV=loops/REVER4 nohup bash abs/stepjlive3.sh 1800 600 > loops/STEPJLIVE3.log 2>&1 &
echo "stepjlive3 $! $(date +%T)" >> loops/AFTERZ6.pids
for A in P2N P2O; do
  if [ -e loops/$A ]; then echo "loops/$A exists, not started" >> loops/AFTERZ6.pids; continue; fi
  if [ $A = P2N ]; then LA="--retry-class --yield-discount 2000 --reexplore 12:0.25"
  else LA="--retry-class --yield-discount 2000 --reexplore 12:0.25 --knn-ctx 10 --head-class"; fi
  [ -s loops/$A.args ] && LA=$(cat loops/$A.args)
  HOURS=5 SET=sets/half2 ARM=$A LOOPARGS="$LA" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
  echo "$A $! $(date +%T) LOOPARGS=$LA" >> loops/AFTERZ6.pids
done
