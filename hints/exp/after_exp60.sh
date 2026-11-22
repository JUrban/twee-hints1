#!/bin/bash
# (22 Nov) Start Z9 (abs/z9.sh: the system from zero on all goals, 6 workers, 8 hours, CPUs 0-20,28-48) 10 minutes
# after exp60 ends, unless loops/Z9.skip appears by then (notes/2026-11-23-z9.md).
cd /project/hintwork
until grep -q "^exp60 done" loops/EXP60.pids; do sleep 30; done
echo "exp60 done seen $(date '+%d %T')" >> loops/Z9.pids
for i in $(seq 1 20); do [ -e loops/Z9.skip ] && { echo "Z9 skipped $(date '+%d %T')" >> loops/Z9.pids; exit 0; }; sleep 30; done
echo "starting Z9 $(date '+%d %T')" >> loops/Z9.pids
nohup bash abs/z9.sh > /dev/null 2>&1 &
echo "Z9 $! $(date +%T)" >> loops/Z9.pids
