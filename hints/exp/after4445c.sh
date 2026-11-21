#!/bin/bash
# (21 Nov 00:56) Replaces abs/afterz6.sh's tail. When exp44/45 end (loops/exp4445.done): production (abs/ul74.sh) at
# J=6 (not 12) beside exp46's arm, the step-join member (abs/stepjlive3.sh), and exp46: P2L = solve_new.sh's
# defaults + --knn-ctx 10 on sets/half2 from zero, 6 workers, 5 hours, against P2K (notes/2026-11-21-knn-ctx.md).
# P2L's LOOPARGS from loops/P2L.args if it is there and not empty (21 Nov 01:37), else --knn-ctx 10.
# Production goes back to J=12 by hand when P2L ends (loops/P2L.done). PIDs in loops/AFTERZ6.pids.
cd /project/hintwork
until [ -e loops/exp4445.done ]; do sleep 60; done
[ -e loops/UL74.log ] && [ ! -e loops/UL74.0420.log ] && mv loops/UL74.log loops/UL74.0420.log
J=6 nohup bash abs/ul74.sh > loops/UL74.out 2>&1 &
echo "ul74 $! $(date +%T)" >> loops/AFTERZ6.pids
REV=loops/REVER4 nohup bash abs/stepjlive3.sh 1800 600 > loops/STEPJLIVE3.log 2>&1 &
echo "stepjlive3 $! $(date +%T)" >> loops/AFTERZ6.pids
[ -e loops/P2L ] && { echo "loops/P2L exists, exp46 not started" >> loops/AFTERZ6.pids; exit 1; }
LA="--knn-ctx 10"; [ -s loops/P2L.args ] && LA=$(cat loops/P2L.args)
HOURS=5 SET=sets/half2 ARM=P2L LOOPARGS="$LA" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2L $! $(date +%T) LOOPARGS=$LA" >> loops/AFTERZ6.pids
