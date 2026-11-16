#!/bin/bash
# (16 Nov 22:15) replaces abs/hou_queue.sh: after HO8b, HO8U (today's context) on its 6 CPUs; once the from-zero
# 4-hour arm LZ4 is done (about 00:05), production at -j 4 (abs/ul37.sh) and the whole benchmark from zero
# (abs/z0_test.sh, 12 workers + 2 transfer).
cd /project/hintwork
until [ -f loops/HO8b.done ]; do sleep 20; done
echo "HO8U started $(date +%T)" >> loops/LVS2.queue
ARM=HO8U nohup bash abs/hou_test.sh > /dev/null 2>&1 &
until [ -f loops/LZ4.done ]; do sleep 20; done
nohup bash abs/ul37.sh > /dev/null 2>&1 &
nohup bash abs/z0_test.sh > /dev/null 2>&1 &
echo "ul37 and Z0 started $(date +%T)" >> loops/LVS2.queue
