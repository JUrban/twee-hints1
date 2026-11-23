#!/bin/bash
# Round 4 of the full loop = round 3's cascade restarted with 6 sibling lemmas (nearest on either side):
# every unsolved goal at most 6 places after a proof gets a 20 s run in the new context first (--cascade-start -1).
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/UL --start 4 --cascade 20,80,320,960 --cascade-start -1 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j 14 --reserve 0 \
  --pool original --wall-factor 15 "$@" --args="--abstract-time 2000" > loops/UL4.log 2>&1
echo "UL4: $(tail -1 loops/UL4.log) $(date +%T)" | tee loops/UL4.done
