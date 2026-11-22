#!/bin/bash
# (22 Nov 10:59) starts abs/exp55.sh when exp54r (the replica pair) ends ("exp54r done" in loops/EXP54R.pids, by
# 16:30), unless loops/EXP55B.skip exists after 10 minutes. exp55's smoke (KDS) was clean.
cd /project/hintwork
T=$(date -d '2026-11-22 16:30' +%s)
until grep -q "^exp54r done" loops/EXP54R.pids 2>/dev/null || [ $(date +%s) -ge $T ]; do sleep 30; done
grep -q "^exp54r done" loops/EXP54R.pids || { echo "exp54r not done by 16:30" >> loops/EXP55.pids; exit 1; }
echo "exp54r done seen $(date '+%d %T')" >> loops/EXP55.pids
D=$(( $(date +%s) + 600 ))
until [ -e loops/EXP55B.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/EXP55B.skip ] && { echo "skipped (EXP55B.skip) $(date '+%d %T')" >> loops/EXP55.pids; exit 0; }
echo "starting exp55 $(date '+%d %T')" >> loops/EXP55.pids
exec bash abs/exp55.sh
