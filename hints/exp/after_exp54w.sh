#!/bin/bash
# (22 Nov 11:12) when exp54 ends ("exp54 done" in loops/EXP54.pids, by 13:30): loops/EXP55.skip (abs/after_exp54.sh then
# exits; exp54's replica pair, abs/exp54r.sh, is deferred), exp57 (abs/exp57.sh, about 2 hours), then abs/exp55.sh
# unless loops/EXP55B.skip exists 10 minutes after exp57 ends.
cd /project/hintwork
T=$(date -d '2026-11-22 13:30' +%s)
until grep -q "^exp54 done" loops/EXP54.pids 2>/dev/null || [ $(date +%s) -ge $T ]; do sleep 20; done
grep -q "^exp54 done" loops/EXP54.pids || { echo "exp54 not done by 13:30" >> loops/EXP57.pids; exit 1; }
touch loops/EXP55.skip
bash abs/exp57.sh
D=$(( $(date +%s) + 600 ))
until [ -e loops/EXP55B.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/EXP55B.skip ] && { echo "exp55 skipped (EXP55B.skip) $(date '+%d %T')" >> loops/EXP55.pids; exit 0; }
echo "starting exp55 after exp57 $(date '+%d %T')" >> loops/EXP55.pids
exec bash abs/exp55.sh
