#!/bin/bash
# exp42 (20 Nov 11:40): the derived-rule transfer with the ancestry runs uncapped, from zero on half2, 2 hours, 6
# workers: P2F = solve_new.sh's defaults (GIVEN=1) with GIVENARGS="--every 300 -j 2 --cap 200 --same-cap 20 --no-inst"
# (the live loop's hit goals per cycle 60 -> 200; the same-statement runs get their own 20), against exp41's P2E
# (the defaults, --cap 60 shared: 20,152 at 2 hours; exp40's PGE on half1 also lacked --no-inst, so it is no control).
# notes/2026-11-20-given-cap.md
cd /project/hintwork
GIVENARGS="--every 300 -j 2 --cap 200 --same-cap 20 --no-inst" SET=sets/half2 ARM=P2F bash abs/or_test2.sh
echo "exp42 done $(date +%T)" > loops/exp42.done
