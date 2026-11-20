#!/bin/bash
# (20 Nov 18:44) After Z6 (loops/Z6.done): exp44 (6 workers, 2 h, notes/2026-11-20-retry-class.md), production
# (abs/ul74.sh, J=10, proofs kept) and the step-join member (abs/stepjlive3.sh, bank = all trusted proofs since
# REVER4 stopped). PIDs in loops/AFTERZ6.pids.
cd /project/hintwork
until [ -e loops/Z6.done ]; do sleep 60; done
sleep 120   # (Z6's live loop and transfer end with it)
nohup bash abs/exp44.sh > loops/exp44.out 2>&1 &
echo "exp44 $!" > loops/AFTERZ6.pids
[ -e loops/UL74.log ] && [ ! -e loops/UL74.0420.log ] && mv loops/UL74.log loops/UL74.0420.log   # (the 04:15-15:30 run's log)
J=10 nohup bash abs/ul74.sh > loops/UL74.out 2>&1 &
echo "ul74 $!" >> loops/AFTERZ6.pids
REV=loops/REVER4 nohup bash abs/stepjlive3.sh 1800 600 > loops/STEPJLIVE3.log 2>&1 &
echo "stepjlive3 $!" >> loops/AFTERZ6.pids
echo "launched $(date +%T)" >> loops/AFTERZ6.pids
