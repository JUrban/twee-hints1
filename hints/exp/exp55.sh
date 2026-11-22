#!/bin/bash
# (22 Nov 09:33) exp55: --knn-drift 5 from zero, side by side with the control (notes/2026-11-22-knn-drift.md).
# sets/half2, 4 workers each, 6 hours, abs/or_test2.sh (SCHED=, transfer every 5 minutes, solve_new.sh's defaults).
cd /project/hintwork
for a in P2X P2Z; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
J=4 HOURS=6 SET=sets/half2 ARM=P2X LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2X $! $(date +%T)" >> loops/EXP55.pids
J=4 HOURS=6 SET=sets/half2 ARM=P2Z LOOPARGS="--knn-drift 5" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2Z $! $(date +%T)" >> loops/EXP55.pids
wait
echo "exp55 done $(date +%T)" >> loops/EXP55.pids
