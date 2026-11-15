#!/bin/bash
# V2p round 4 = round 3 redone with twee-e20 (round 3's resumed runs were blind: new lemmas gave the problem a second
# signature). The 6 unsolved resume their round-3 states; +900 abstract s, CPU cap 3600 s, stall gap 60 s
until [ -s /project/hintwork/loops/U3po.done ]; do sleep 30; done
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/v2_hard loops/V2p --start 4 --rounds 1 --timeout 300,300,900,900,900 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e20 --keep-out --resume -j 6 --pool original \
  --args="--abstract-time 2000 --max-cpu 3600 --eqhint-stall-cps 120000" > loops/V2p_r4.log 2>&1
echo "V2p r4: $(tail -1 loops/V2p_r4.log) $(date +%T)" | tee loops/V2p_r4.done
