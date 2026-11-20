#!/bin/bash
# exp41 (20 Nov 09:2x): replication of exp40 on half2 (the other 65 originals, 25,847 goals), from zero, 2 hours, 6
# workers: P2E = solve_new.sh's defaults now (GIVEN=1: loop.py --given-scan loops/P2E_GF + givenmatch.py live
# loops/P2E_GML), against exp30's P2D (19 Nov 12:45, the same script without GIVEN: 19,383 at 2 hours).
# notes/2026-11-20-half2-given.md
cd /project/hintwork
SET=sets/half2 ARM=P2E bash abs/or_test2.sh
echo "exp41 done $(date +%T)" > loops/exp41.done
