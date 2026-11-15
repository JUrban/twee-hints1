#!/bin/bash
# Sketches with laws that do not trivialise (15 Nov 19:10; user asked what sketches were, 2ab: laws made every sketch
# trivial). sets/gen48 (first 48 of gen200, unsolved at 14:31), snapshot loops/ULsW, 1 worker per arm.
#   ARM=CL6A: CL5's config (8 nearest unproven siblings + 8 kNN goals, fill 3 s; true assumptions only)
#   ARM=CL6B X="--laws --min-sketch-steps 50": + laws; a law sketch with < 50 proof steps bans its laws for the target
#   ARM=CL6C: control, fresh 20 s (the climb's final run)
cd /project/hintwork
L="--init loops/ULsW --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15"
if [ "$ARM" = CL6C ]; then
  python3 -u /project/twee/hints/loop.py sets/gen48 loops/$ARM $L --start 1 --rounds 1 --keep-out -j 1 --timeout 20 \
    --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider" > loops/$ARM.log 2>&1
  echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/48 $(date +%T)" | tee loops/$ARM.done
else
  python3 /project/twee/hints/climb.py sets/gen48 loops/$ARM --m 8 --knn 8 --runs 12 --sketch-time 5 --final-time 20 --fill 3 -j 1 $X -- \
    $L --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
  echo "$ARM $(tail -1 loops/$ARM.log) $(date +%T)" | tee loops/$ARM.done
fi
