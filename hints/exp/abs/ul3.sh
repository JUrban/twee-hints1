#!/bin/bash
# full-benchmark loop, after round 2: cascade scheduling (retries after new nearby proofs at 20 s,
# frontier deepening 80 / 320 / 960 abstract s with saved states), 14 cores.
# usage: ul3.sh [extra loop.py args]; lemmas from both sides, so goals that gain lemmas from above get a first 20 s run (--cascade-was-below)
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/UL --start 3 --cascade 20,80,320,960 --cascade-start 0 --cascade-was-below \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e22 --keep-out -j 14 --reserve 0 \
  --pool original --wall-factor 15 --lemma-after "$@" --args="--abstract-time 2000" > loops/UL3.log 2>&1
echo "UL3 $(tail -1 loops/UL3.log) $(date +%T)" | tee loops/UL3.done
