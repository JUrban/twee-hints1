#!/bin/bash
# after V2p round 4: frequency-weighted hint factors on the 189-goal aK2_eq_aK3_a prefix (whole pool online: 60 solved)
until [ -s /project/hintwork/loops/V2p_r4.done ]; do sleep 30; done
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e20 --keep-out -j 5 --pool original --online"
A="--abstract-time 2000 --max-cpu 200"
python3 /project/twee/hints/loop.py sets/u3a189 loops/U3af $C --freq-factors 1:0.2,4:0.05 --args="$A" > loops/U3af.log 2>&1
python3 /project/twee/hints/loop.py sets/u3a189 loops/U3ag $C --freq-factors 1:1,2:0.1 --args="$A" > loops/U3ag.log 2>&1 &
wait
for v in U3af U3ag; do echo "$v $(tail -1 loops/$v.log)"; done
