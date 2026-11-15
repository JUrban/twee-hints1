#!/bin/bash
# Goal-directed twee options (15 Nov 19:15; twee's completion barely depends on the goal, REPORT 2ai): fresh 20 s on
# sets/gen48 from loops/ULsW, as CL6C (the control).  ARM=BG1 X="--backwards-goal 1"; ARM=HG X="--hint-goal"
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/gen48 loops/$ARM --init loops/ULsW --start 1 --rounds 1 --keep-out -j ${J:-1} --timeout 20 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --max-cpu 200 --no-eqhint-consider $X" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/r1/results.tsv)/48 $(date +%T)" | tee loops/$ARM.done
