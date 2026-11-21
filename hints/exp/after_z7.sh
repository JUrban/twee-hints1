#!/bin/bash
# exp52 (21 Nov, notes/2026-11-21-floor-ratio.md): when Z7 ends (loops/Z7.done), two half2 arms from zero, 4 workers
# each, 3 hours, both on solve_new.sh's defaults (LATE = P2O's set): P2T the control, P2U + --floor-ratio 20. Waits at
# most until 22:30.
cd /project/hintwork
T=$(date -d '2026-11-21 22:30' +%s)
until [ -e loops/Z7.done ] || [ $(date +%s) -ge $T ]; do sleep 30; done
[ -e loops/Z7.done ] || { echo "no Z7.done by 22:30"; exit 1; }
for a in P2T P2U; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
J=4 HOURS=3 SET=sets/half2 ARM=P2T LOOPARGS="" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2T $! $(date +%T)" >> loops/AFTERZ7.pids
J=4 HOURS=3 SET=sets/half2 ARM=P2U LOOPARGS="--floor-ratio 20" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2U $! $(date +%T)" >> loops/AFTERZ7.pids
wait
echo "exp52 done $(date +%T)" >> loops/AFTERZ7.pids
