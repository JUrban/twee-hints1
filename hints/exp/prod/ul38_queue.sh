#!/bin/bash
# (16 Nov 20:00) when XFR3L is done and merged: production from -j 4 (ul37) to -j 6 (ul38).
cd /project/hintwork
until [ -f loops/XFR3L.merge ]; do sleep 30; done
B=$(ps -eo pid,args | awk '$2=="bash" && $3=="abs/ul37.sh" {print $1}')
P=$(ps -eo pid,args | awk '$0 ~ /loop.py sets\/all loops\/UL / && $0 !~ /awk/ {print $1}')
kill $B $P
sleep 2
C=$(ps -eo pid,args | awk '$0 ~ /loops\/UL\/tmp\// && $0 !~ /awk/ {print $1}')
[ -n "$C" ] && kill $C
sleep 3
nohup bash abs/ul38.sh > /dev/null 2>&1 &
echo "ul38 started $(date +%T); XFR3L: $(tail -n 1 loops/XFR3L.merge)" > loops/UL38.queue
