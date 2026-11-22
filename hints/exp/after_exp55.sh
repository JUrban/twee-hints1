#!/bin/bash
# (22 Nov 15:33) when exp55 ends ("exp55 done" in loops/EXP55.pids), wait 10 minutes for loops/EXP60.skip, then run exp60.
cd /project/hintwork
echo "after_exp55 $$ $(date '+%d %T')" >> loops/EXP60.pids
until grep -q "^exp55 done" loops/EXP55.pids 2>/dev/null; do sleep 30; done
echo "exp55 done seen $(date '+%d %T')" >> loops/EXP60.pids
for i in $(seq 20); do [ -e loops/EXP60.skip ] && { echo "skipped $(date '+%d %T')" >> loops/EXP60.pids; exit 0; }; sleep 30; done
echo "starting exp60 $(date '+%d %T')" >> loops/EXP60.pids
bash abs/exp60.sh
