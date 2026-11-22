#!/bin/bash
# (22 Nov 12:59) exp56c: when the exp58a replay (exp/gmreplay.py, PID 2059788) ends, retry the tried goals still unsolved
# with --lemma-ax and longer passes (--times 60,160: the hits come at given rule 2,000-18,000 of their source runs):
# loops/GMR3 (notes/2026-11-22-gm-retry.md).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
while kill -0 2059788 2>/dev/null; do sleep 20; done
[ -e loops/GMR3 ] && { echo "loops/GMR3 exists"; exit 1; }
echo "GMR3 start $(date '+%d %T')" > loops/GMR3.pids
python3 -u /project/twee/hints/exp/gmretry.py loops/GMR3 -j 1 --lemma-ax --times 60,160 -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 --keep-out "--args=--abstract-time 2000 --no-eqhint-consider" > loops/GMR3.log 2>&1
echo "GMR3 done $(date '+%d %T')" >> loops/GMR3.pids
