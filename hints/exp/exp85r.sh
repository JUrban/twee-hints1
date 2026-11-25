#!/bin/bash
# (25 Nov 08:34) exp85's replay restarted (notes/2026-11-25-precedence-portfolio.md, "Replay with abstract work"): the
# user: an order also dominates another when it proves the same goals much faster. prec_replay.py now records twee's
# WORK line (critical pairs considered, rules), and the cap is abstract: --abstract 5 (twee --max-time 5, 10,000
# considered pairs, production's first cascade level), --cpu 30 only as a safety cap. The first replay's 292 rows
# (CPU cap 10 s, no work counts) are in loops/P85C/replay.v1.tsv.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
echo "replay (abstract 5) start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/P85C/cap loops/P85C/replay.tsv --goals loops/P85C/dev.txt \
  --orders /project/twee/hints/exp/sets/exp85.orders -j 5 --cpu 30 --abstract 5 >> loops/EXP85.pids 2>&1
echo "exp85 done $(date '+%d %T')" >> loops/EXP85.pids
