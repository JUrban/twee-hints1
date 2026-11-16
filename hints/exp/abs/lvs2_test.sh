#!/bin/bash
# The learned scheduler with --sweep-first (16 Nov 20:10): as LVS (972), with solve_new.sh's SCHED default, which now has
# --sweep-first (never-run goals first, in goal order). ARM=LVS2.
# Runs a private copy of solve_new.sh (edits to the original must not reach a running bash).
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
EXCLUDE=originals LOOPARGS= \
  bash loops/$ARM.solve_new.sh sets/rp3 loops/ALL loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done
