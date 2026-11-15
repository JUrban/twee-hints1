#!/bin/bash
# multi-goal windows (twee-e21 --multi-goal, loop.py --multi W) on the 189-goal aK2_eq_aK3_a prefix,
# same config as U3po (online whole pool, 20 s per goal, rm4t, lemmas 3+10): po solved 60
while kill -0 704843 2>/dev/null; do sleep 30; done   # U3af
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e21 --keep-out -j 5 --pool original --online"
A="--abstract-time 2000 --max-cpu 200"
for W in 5 10; do
  python3 /project/twee/hints/loop.py sets/u3a189 loops/U3am$W $C --multi $W --args="$A" > loops/U3am$W.log 2>&1
  echo "U3am$W $(tail -1 loops/U3am$W.log) $(date +%T)" | tee loops/U3am$W.done
done
