#!/bin/bash
# exp54 (22 Nov 03:02, notes/2026-11-22-late-ab.md): the late A/B. sets/late2 (the 3,817 half2 goals Z7 left
# unsolved) with loops/Z7's proofs as the context, 4 workers each, 3 hours, side by side: LAA the control (solve_new.sh's
# defaults), LAB + --head-time 20 (exp51, notes/2026-11-21-head-time.md).
cd /project/hintwork
for a in LAA LAB; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
ARM=LAA LOOPARGS="" nohup bash abs/late_test.sh > /dev/null 2>&1 &
echo "LAA $! $(date +%T)" >> loops/EXP54.pids
ARM=LAB LOOPARGS="--head-time 20" nohup bash abs/late_test.sh > /dev/null 2>&1 &
echo "LAB $! $(date +%T)" >> loops/EXP54.pids
wait
echo "exp54 done $(date +%T)" >> loops/EXP54.pids
