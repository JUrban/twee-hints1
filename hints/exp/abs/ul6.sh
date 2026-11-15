#!/bin/bash
# Round 5 continued (14 Nov 19:35) with --no-resume-requeue: on sets/fr100 (100 UL r4 frontier failures, 4 x 20 s
# by resume) BRSn (no requeue) 29 vs BRS (requeue) 23 at the same wall time, BRS-only 0 (REPORT 2w).
# --cascade-continue: the levels round 5 already tried are read from loops/UL/r5/results.tsv. -j 16 (BRS ends soon).
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 20,80,320,960 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j 16 --reserve 0 \
  --pool original --wall-factor 15 "$@" --args="--abstract-time 2000 --no-resume-requeue" > loops/UL6.log 2>&1
echo "UL6: $(tail -1 loops/UL6.log) $(date +%T)" | tee loops/UL6.done
