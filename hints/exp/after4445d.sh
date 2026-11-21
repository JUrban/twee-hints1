#!/bin/bash
# (21 Nov 02:03) Replaces abs/after4445c.sh. When exp44/45 end (loops/exp4445.done): production (abs/ul74.sh) at J=4
# beside two half2 arms, the step-join member (abs/stepjlive3.sh), and the arms from zero, 6 workers, 5 hours:
#   P2L (exp46, notes/2026-11-21-knn-ctx.md): LOOPARGS from loops/P2L.args, else --knn-ctx 10;
#   P2M (exp47, notes/2026-11-21-head-class.md): LOOPARGS from loops/P2M.args, else --head-class.
# Production goes back to J=12 by hand when they end. PIDs in loops/AFTERZ6.pids.
cd /project/hintwork
until [ -e loops/exp4445.done ]; do sleep 60; done
[ -e loops/UL74.log ] && [ ! -e loops/UL74.0420.log ] && mv loops/UL74.log loops/UL74.0420.log
J=4 nohup bash abs/ul74.sh > loops/UL74.out 2>&1 &
echo "ul74 $! $(date +%T)" >> loops/AFTERZ6.pids
REV=loops/REVER4 nohup bash abs/stepjlive3.sh 1800 600 > loops/STEPJLIVE3.log 2>&1 &
echo "stepjlive3 $! $(date +%T)" >> loops/AFTERZ6.pids
for A in P2L P2M; do
  if [ -e loops/$A ]; then echo "loops/$A exists, not started" >> loops/AFTERZ6.pids; continue; fi
  if [ $A = P2L ]; then LA="--knn-ctx 10"; else LA="--head-class"; fi
  [ -s loops/$A.args ] && LA=$(cat loops/$A.args)
  HOURS=5 SET=sets/half2 ARM=$A LOOPARGS="$LA" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
  echo "$A $! $(date +%T) LOOPARGS=$LA" >> loops/AFTERZ6.pids
done
