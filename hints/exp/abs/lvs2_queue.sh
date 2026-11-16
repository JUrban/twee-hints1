#!/bin/bash
# (16 Nov 20:10) when XFR3L is done and merged: production (ul37, -j 4) pauses, LVS2 runs 1 hour; then production
# resumes at -j 6 (ul38).
cd /project/hintwork
until [ -f loops/XFR3L.merge ]; do sleep 30; done
B=$(ps -eo pid,args | awk '$2=="bash" && $3=="abs/ul37.sh" {print $1}')
P=$(ps -eo pid,args | awk '$0 ~ /loop.py sets\/all loops\/UL / && $0 !~ /awk/ {print $1}')
kill $B $P
sleep 2
C=$(ps -eo pid,args | awk '$0 ~ /loops\/UL\/tmp\// && $0 !~ /awk/ {print $1}')
[ -n "$C" ] && kill $C
echo "production paused $(date +%T); XFR3L: $(tail -n 1 loops/XFR3L.merge)" > loops/LVS2.queue
ARM=LVS2 bash abs/lvs2_test.sh
nohup bash abs/ul38.sh > /dev/null 2>&1 &
echo "ul38 started $(date +%T)" >> loops/LVS2.queue
