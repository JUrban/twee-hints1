#!/bin/bash
# (22 Nov 00:23) After exp53 ("exp53 done" in loops/EXP53.pids; at most until 04:00): wait up to 20 minutes for
# loops/Z8.go (start now; a default installed first is in Z8) or loops/Z8.skip (do not start), then start abs/z8.sh
# (with the defaults as they are if neither file appears).
cd /project/hintwork
T=$(date -d '2026-11-22 04:00' +%s)
until grep -q "^exp53 done" loops/EXP53.pids 2>/dev/null || [ $(date +%s) -ge $T ]; do sleep 30; done
grep -q "^exp53 done" loops/EXP53.pids || { echo "exp53 not done by 04:00" >> loops/Z8.pids; exit 1; }
D=$(( $(date +%s) + 1200 ))
until [ -e loops/Z8.go ] || [ -e loops/Z8.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/Z8.skip ] && { echo "skipped $(date '+%d %T')" >> loops/Z8.pids; exit 0; }
echo "starting Z8 $(date '+%d %T') ($( [ -e loops/Z8.go ] && echo go file || echo no decision file))" >> loops/Z8.pids
exec bash abs/z8.sh
