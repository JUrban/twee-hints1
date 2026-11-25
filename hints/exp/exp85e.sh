#!/bin/bash
# (25 Nov 13:07) exp85e: 4 orders at 80,000 pairs each against the default at 320,000 on the 22 goals neither order 0
# nor 60 proved within 80,000 (notes/2026-11-25-precedence-portfolio.md, "exp85e").
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
O=/project/twee/hints/exp/sets
echo "exp85e start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/P85C/cap loops/P85C/e85p.tsv --goals $O/exp85e.goals --orders $O/exp85e.orders \
  -j 10 --cpu 300 --abstract 40 >> loops/EXP85.pids 2>&1
python3 -u /project/twee/hints/exp/prec_replay.py loops/P85C/cap loops/P85C/e85d.tsv --goals $O/exp85e.goals --orders $O/exp85e.def.orders \
  -j 10 --cpu 900 --abstract 160 >> loops/EXP85.pids 2>&1
echo "exp85e done $(date '+%d %T')" >> loops/EXP85.pids
