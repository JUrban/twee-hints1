#!/bin/bash
# (22 Nov 15:33) exp60: --floor-ratio-until 120 from zero, side by side with the control (notes/2026-11-22-floor-ratio-until.md).
# sets/half2, 4 workers each, 6 hours, abs/or_test2.sh (SCHED=, transfer every 5 minutes, solve_new.sh's defaults).
cd /project/hintwork
for a in P3A P3B; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
J=4 HOURS=6 SET=sets/half2 ARM=P3A LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P3A $! $(date +%T)" >> loops/EXP60.pids
J=4 HOURS=6 SET=sets/half2 ARM=P3B LOOPARGS="--floor-ratio-until 120" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P3B $! $(date +%T)" >> loops/EXP60.pids
wait
echo "exp60 done $(date +%T)" >> loops/EXP60.pids
