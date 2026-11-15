#!/bin/bash
# lemmas from proven siblings above the goal too (loop.py --lemma-after), on the 222 goals of sets/u3 that the
# online whole-pool run (U3po) left unsolved but that have a proven sibling at most 10 above; init = U3po's proofs.
# Control: the same without --lemma-after on a random 74 of them.
until [ -s /project/hintwork/loops/U3am5.done ]; do sleep 30; done
cd /project/hintwork
C="--init loops/U3poI --start 1 --rounds 1 --timeout 20 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e21 --keep-out -j 5 --pool original --online --wall-factor 15"
A="--abstract-time 2000 --max-cpu 200"
python3 /project/twee/hints/loop.py sets/u3after loops/U3la $C --lemma-after --args="$A" > loops/U3la.log 2>&1
echo "U3la $(tail -1 loops/U3la.log) $(date +%T)" | tee loops/U3la.done
python3 /project/twee/hints/loop.py sets/u3after74 loops/U3lb $C --args="$A" > loops/U3lb.log 2>&1
echo "U3lb $(tail -1 loops/U3lb.log) $(date +%T)" | tee loops/U3lb.done
