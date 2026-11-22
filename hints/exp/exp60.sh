#!/bin/bash
# (22 Nov 15:33) exp60: --floor-ratio-until 120 from zero, side by side with the control (notes/2026-11-22-floor-ratio-until.md).
# sets/half2, 4 workers each, 6 hours, abs/or_test2.sh (SCHED=, transfer every 5 minutes, solve_new.sh's defaults).
cd /project/hintwork
for a in P3A P3B P3C; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
J=4 HOURS=6 SET=sets/half2 ARM=P3A LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P3A $! $(date +%T)" >> loops/EXP60.pids
J=4 HOURS=6 SET=sets/half2 ARM=P3B LOOPARGS="--floor-ratio-until 120" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P3B $! $(date +%T)" >> loops/EXP60.pids
# (18:28) a third arm on the same control: --knn-drift 5 with --knn-drift-after 60 (exp55's drift retries cost 216 at
# 30 minutes and gave +109 to +122 from 2 hours; a replica of exp55 too, notes/2026-11-22-knn-drift.md)
J=4 HOURS=6 SET=sets/half2 ARM=P3C LOOPARGS="--knn-drift 5 --knn-drift-after 60" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P3C $! $(date +%T)" >> loops/EXP60.pids
wait
echo "exp60 done $(date +%T)" >> loops/EXP60.pids
