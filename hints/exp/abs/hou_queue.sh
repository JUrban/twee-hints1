#!/bin/bash
# (16 Nov 22:05) replaces abs/lvs2_queue2.sh's last step: after HO8b, HO8U (today's context) on its 6 CPUs;
# production (abs/ul38.sh, -j 6) once the from-zero 4-hour arm LZ4 is done (about 00:05).
cd /project/hintwork
until [ -f loops/HO8b.done ]; do sleep 20; done
echo "HO8U started $(date +%T)" >> loops/LVS2.queue
ARM=HO8U nohup bash abs/hou_test.sh > /dev/null 2>&1 &
until [ -f loops/LZ4.done ]; do sleep 20; done
nohup bash abs/ul38.sh > /dev/null 2>&1 &
echo "ul38 started $(date +%T)" >> loops/LVS2.queue
