#!/bin/bash
# (22 Nov 11:27) exp56b: when GMR (exp/gmretry.py, PID 2023224) ends, the same retry with --lemma-ax (the source runs'
# lemma axioms in the sketches' .ax, named by their proven goal) on every tried goal still unsolved: loops/GMR2.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
while kill -0 2023224 2>/dev/null; do sleep 20; done
[ -e loops/GMR2 ] && { echo "loops/GMR2 exists"; exit 1; }
echo "GMR2 start $(date '+%d %T')" > loops/GMR2.pids
python3 -u /project/twee/hints/exp/gmretry.py loops/GMR2 -j 1 --lemma-ax -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 --keep-out "--args=--abstract-time 2000 --no-eqhint-consider" > loops/GMR2.log 2>&1
echo "GMR2 done $(date '+%d %T')" >> loops/GMR2.pids
