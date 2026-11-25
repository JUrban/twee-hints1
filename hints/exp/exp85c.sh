#!/bin/bash
# (25 Nov 09:48) exp85b's replay resumed with -j 10 (CLS71 and CLQ83 idle: CLS71 has no targets left since 09:45). The
# same command as exp85b.sh step 4; prec_replay.py skips the rows already in loops/P85D/replay.tsv.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
echo "exp85b replay (-j 10) start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/P85D/cap loops/P85D/replay.tsv --goals loops/P85D/dev.txt \
  --orders /project/twee/hints/exp/sets/exp85.orders -j 10 --cpu 60 --abstract 10 >> loops/EXP85.pids 2>&1
echo "exp85b done $(date '+%d %T')" >> loops/EXP85.pids
