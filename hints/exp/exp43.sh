#!/bin/bash
# exp43 (20 Nov, after exp42): the live loop runs a derived-rule hit without waiting for the loop to fail on its goal
# (givenmatch.py --no-wait), from zero on half2, 2 hours, 6 workers: P2G = exp42's P2F setting (GIVENARGS "--every 300
# -j 2 --cap 200 --same-cap 20 --no-inst") plus --no-wait, against P2F. In exp42 the ancestry runs proved 93% at about
# 4 s each while 120-300 hits waited for the loop's failure. notes/2026-11-20-given-nowait.md
cd /project/hintwork
GIVENARGS="--every 300 -j 2 --cap 200 --same-cap 20 --no-wait --no-inst" SET=sets/half2 ARM=P2G bash abs/or_test2.sh
echo "exp43 done $(date +%T)" > loops/exp43.done
