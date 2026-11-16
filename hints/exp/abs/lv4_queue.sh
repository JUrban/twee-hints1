#!/bin/bash
# (16 Nov 19:05) after LVS: production to -j 4 (abs/ul37.sh), then the 4-hour arms LV4 (clean public context) and
# LZ4 (from zero). They get the learned scheduler only if LVS beat LVD (942) by 10 or more.
cd /project/hintwork
until [ -f loops/LVS.done ]; do sleep 20; done
n=$(python3 abs/totcurve.py sets/rp3 LVS | awk '{print $NF}')
SCHED="--sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400"
if [ "$n" -ge 952 ]; then LA="$SCHED"; else LA=""; fi
echo "LVS $n; LOOPARGS='$LA' $(date +%T)" > loops/LV4.queue
B=$(ps -eo pid,args | awk '$2=="bash" && $3=="abs/ul36.sh" {print $1}')
P=$(ps -eo pid,args | awk '$0 ~ /loop.py sets\/all loops\/UL / && $0 !~ /awk/ {print $1}')
kill $B $P
sleep 2
C=$(ps -eo pid,args | awk '$0 ~ /loops\/UL\/tmp\// && $0 !~ /awk/ {print $1}')
[ -n "$C" ] && kill $C
sleep 3
nohup bash abs/ul37.sh > /dev/null 2>&1 &
ARM=LV4 CTX=loops/ALL LOOPARGS="$LA" nohup bash abs/lv4_test.sh > /dev/null 2>&1 &
ARM=LZ4 CTX=loops/EMPTY LOOPARGS="$LA" nohup bash abs/lv4_test.sh > /dev/null 2>&1 &
echo "started $(date +%T)" >> loops/LV4.queue
