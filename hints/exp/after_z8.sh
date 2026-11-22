#!/bin/bash
# (22 Nov 03:02) After Z8 (loops/Z8.done; at most until 12:00): wait up to 20 minutes for loops/EXP54.go (start now)
# or loops/EXP54.skip (do not start), then start abs/exp54.sh (also if neither file appears).
cd /project/hintwork
T=$(date -d '2026-11-22 12:00' +%s)
until [ -e loops/Z8.done ] || [ $(date +%s) -ge $T ]; do sleep 30; done
[ -e loops/Z8.done ] || { echo "Z8 not done by 12:00" >> loops/EXP54.pids; exit 1; }
echo "Z8 done $(date '+%d %T')" >> loops/EXP54.pids
D=$(( $(date +%s) + 1200 ))
until [ -e loops/EXP54.go ] || [ -e loops/EXP54.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/EXP54.skip ] && { echo "skipped $(date '+%d %T')" >> loops/EXP54.pids; exit 0; }
echo "starting exp54 $(date '+%d %T') ($( [ -e loops/EXP54.go ] && echo go file || echo no decision file))" >> loops/EXP54.pids
exec bash abs/exp54.sh
