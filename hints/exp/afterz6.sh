#!/bin/bash
# (20 Nov 19:38) After Z6 (loops/Z6.done): exp44 + exp45 (abs/exp4445.sh: three half2 arms, 6 workers each, 5 hours;
# notes/2026-11-20-retry-class.md, notes/2026-11-20-yield-discount.md). When they end: production (abs/ul74.sh, J=12,
# proofs kept; the 04:15 run's log kept as UL74.0420.log) and the step-join member (abs/stepjlive3.sh, cycles after
# JOIN/c5). PIDs in loops/AFTERZ6.pids.
cd /project/hintwork
until [ -e loops/Z6.done ]; do sleep 60; done
sleep 120   # (Z6's live loop and transfer end with it)
nohup bash abs/exp4445.sh > loops/exp4445.out 2>&1 &
echo "exp4445 $! $(date +%T)" > loops/AFTERZ6.pids
until [ -e loops/exp4445.done ]; do sleep 60; done
[ -e loops/UL74.log ] && [ ! -e loops/UL74.0420.log ] && mv loops/UL74.log loops/UL74.0420.log
J=12 nohup bash abs/ul74.sh > loops/UL74.out 2>&1 &
echo "ul74 $! $(date +%T)" >> loops/AFTERZ6.pids
REV=loops/REVER4 nohup bash abs/stepjlive3.sh 1800 600 > loops/STEPJLIVE3.log 2>&1 &
echo "stepjlive3 $! $(date +%T)" >> loops/AFTERZ6.pids
