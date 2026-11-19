#!/bin/bash
# exp30 (19 Nov 12:45): replication of exp29 on half2 (the other 65 originals, 25,847 goals), from zero, 2 hours, 6
# workers each, both arms at once: P2A = the 17 Nov system (PGA's setting: twee-e48, PG 0.25, cascade 5,20,80,320, no
# deep portfolio), P2D = solve_new.sh's new defaults (PGD's setting). notes/2026-11-19-half2-replication.md
cd /project/hintwork
SET=sets/half2 ARM=P2A DEEP= CASCADE=5,20,80,320 TWEE=/project/bin/twee-e48 bash abs/or_test2.sh &
SET=sets/half2 ARM=P2D bash abs/or_test2.sh &
wait
