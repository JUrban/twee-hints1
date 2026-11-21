#!/bin/bash
# (21 Nov 22:25) After exp52 (loops/P2T.done and loops/P2U.done; at most until 01:00): wait up to 20 minutes for a
# decision file, then start exp53 (abs/exp53.sh). loops/EXP53.go: start now (if exp52's option was installed as a
# default in solve_new.sh, both exp53 arms have it). loops/EXP53.skip: do not start. Neither: start with the
# defaults as they are.
cd /project/hintwork
T=$(date -d '2026-11-22 01:00' +%s)
until { [ -e loops/P2T.done ] && [ -e loops/P2U.done ]; } || [ $(date +%s) -ge $T ]; do sleep 30; done
{ [ -e loops/P2T.done ] && [ -e loops/P2U.done ]; } || { echo "exp52 not done by 01:00" >> loops/EXP53.pids; exit 1; }
echo "exp52 done $(date '+%d %T')" >> loops/EXP53.pids
D=$(( $(date +%s) + 1200 ))
until [ -e loops/EXP53.go ] || [ -e loops/EXP53.skip ] || [ $(date +%s) -ge $D ]; do sleep 15; done
[ -e loops/EXP53.skip ] && { echo "skipped $(date '+%d %T')" >> loops/EXP53.pids; exit 0; }
echo "starting exp53 $(date '+%d %T') ($( [ -e loops/EXP53.go ] && echo go file || echo no decision file))" >> loops/EXP53.pids
exec bash abs/exp53.sh
