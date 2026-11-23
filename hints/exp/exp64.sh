#!/bin/bash
# (23 Nov) exp64 (notes/2026-11-23-plain-level.md): a plain level (loop.py --variants plk100s40@0: no hints, no rule
# model, no PG, 100 kNN and 40 sibling lemmas, 5 s) from zero, side by side with the control. sets/half2, 4 workers
# each, 6 hours, abs/or_test3.sh (CPU sets as exp60's pins: whole cores on both sockets), solve_new.sh's defaults.
# P4B's DEEP is solve_new.sh's with plk100s40@0 after unf@0, a prior of 3 and in --explore-labels.
# Starts 5 minutes after Z9 ends (loops/Z9.done), in Z9's place; loops/Z9C.skip keeps Z9C from starting.
cd /project/hintwork
until [ -e loops/Z9.done ]; do sleep 30; done
sleep 300
while ps -eo args | grep -q "[l]oops/Z9 "; do sleep 30; done
for a in P4A P4B; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
CPUSET="0-6,28-34" J=4 HOURS=6 SET=sets/half2 ARM=P4A LOOPARGS="" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "P4A $! $(date '+%d %T')" >> loops/EXP64.pids
DEEP="--chain-level 1 --variants unf@0,plk100s40@0,k60@0,k100@0,k200@0,k400@0,kd@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1,Vplk100s40@0=3 --ratio-order --explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0,Vplk100s40@0" \
  CPUSET="7-13,35-41" J=4 HOURS=6 SET=sets/half2 ARM=P4B LOOPARGS="" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "P4B $! $(date '+%d %T')" >> loops/EXP64.pids
wait
echo "exp64 done $(date '+%d %T')" >> loops/EXP64.pids
