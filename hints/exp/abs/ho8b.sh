#!/bin/bash
# (16 Nov 20:15) The 8 whole holdout originals of sets/ho8 (3,400 goals) from scratch again, as abs/ho8.sh (HO8 2451,
# 1 hour, 4 workers, clean context loops/ALL), with solve_new.sh's defaults of 20:05: the learned scheduler with
# --sweep-first and the transfer every 2 minutes. With LVS2 on sets/rp3 it updates the 11-original figure (71.7%).
# Runs a private copy of solve_new.sh.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/HO8b.solve_new.sh
EXCLUDE=originals bash loops/HO8b.solve_new.sh sets/ho8 loops/ALL loops/HO8b 4 1 > loops/HO8b.out 2>&1
touch loops/HO8b.done
