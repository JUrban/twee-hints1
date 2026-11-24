#!/bin/bash
# (24 Nov 00:17) exp75: hourly replay of the climbers' conditional proofs of unsolved targets whose assumptions production has
# since proved (exp/condreplay.py; notes/2026-11-24-cond-replay.md). Context: the newest loops/TRUSTNOW/t*.trusted.
# Proofs go through condimport.py (rerun, every USEDAXIOMS name a trusted goal, printed proof) into loops/CRP75 and
# merge.py into loops/UL. A proof tried once is not tried again (cond/CRP75/tried.tsv). 2 threads only when one is
# ready; the scan itself takes seconds.
cd /project/hintwork
mkdir -p cond/CRP75
while true; do
  TR=$(ls -t loops/TRUSTNOW/t*.trusted | head -1)
  D=cond/CRP75/r$(date +%d%H%M)
  DIRS=$(ls -d loops/*/used.tsv | sed 's,/used.tsv,,')
  python3 -u /project/twee/hints/exp/condreplay.py $D $DIRS --trusted $TR -j 2 --time 60 --tried cond/CRP75/tried.tsv > $D.log 2>&1
  if grep -q -P '\tTHM\t' $D/results.tsv 2>/dev/null; then
    python3 /project/twee/hints/exp/condimport.py $D loops/CRP75 --trusted $TR --time 60 > $D.import 2>&1
    flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CRP75 > $D.merge 2>&1
  fi
  echo "$(date '+%d %T') $D $TR | $(head -1 $D.log) | $(tail -1 $D.log)" >> cond/CRP75.status
  sleep 3600
done
