#!/bin/bash
# (16 Nov 23:45) replaces abs/z0_queue.sh: Z0 (the whole benchmark from zero, 12 workers + 2 transfer) as soon as
# HO8U is done; production at -j 4 (abs/ul37.sh) once LZ4's last runs end.
cd /project/hintwork
until [ -f loops/HO8U.done ]; do sleep 20; done
nohup bash abs/z0_test.sh > /dev/null 2>&1 &
echo "Z0 started $(date +%T)" >> loops/LVS2.queue
until [ -f loops/LZ4.done ]; do sleep 20; done
nohup bash abs/ul37.sh > /dev/null 2>&1 &
echo "ul37 started $(date +%T)" >> loops/LVS2.queue
