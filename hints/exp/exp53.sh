#!/bin/bash
# exp53 (21 Nov, notes/2026-11-21-renorm-zero.md): the queue never renormalised, from zero. Two half2 arms, 4 workers
# each, 3 hours, both on solve_new.sh's defaults: P2V the control, P2W + PG="--cp-renormalise-threshold 1000" (solve_new.sh
# passes $PG into the main loop's twee arguments; the transfer and derived-rule loops are the same in both arms).
cd /project/hintwork
for a in P2V P2W; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
J=4 HOURS=3 SET=sets/half2 ARM=P2V LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2V $! $(date +%T)" >> loops/EXP53.pids
PG="--cp-renormalise-threshold 1000" J=4 HOURS=3 SET=sets/half2 ARM=P2W LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2W $! $(date +%T)" >> loops/EXP53.pids
wait
echo "exp53 done $(date +%T)" >> loops/EXP53.pids
