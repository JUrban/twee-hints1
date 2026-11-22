#!/bin/bash
# (22 Nov 09:33) starts abs/exp55.sh when exp54 ends ("exp54 done" in loops/EXP54.pids, by 13:30), after up to 20
# minutes for loops/EXP55.go or loops/EXP55.skip (exp54's result may call for its replica pair first).
cd /project/hintwork
T=$(date -d '2026-11-22 13:30' +%s)
until grep -q "^exp54 done" loops/EXP54.pids 2>/dev/null || [ $(date +%s) -ge $T ]; do sleep 30; done
grep -q "^exp54 done" loops/EXP54.pids || { echo "exp54 not done by 13:30" >> loops/EXP55.pids; exit 1; }
echo "exp54 done seen $(date '+%d %T')" >> loops/EXP55.pids
D=$(( $(date +%s) + 1200 ))
until [ -e loops/EXP55.go ] || [ -e loops/EXP55.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/EXP55.skip ] && { echo "skipped $(date '+%d %T')" >> loops/EXP55.pids; exit 0; }
[ -e loops/EXP55.go ] || { echo "no go file by $(date '+%d %T'): not started" >> loops/EXP55.pids; exit 0; }
echo "starting exp55 $(date '+%d %T')" >> loops/EXP55.pids
exec bash abs/exp55.sh
