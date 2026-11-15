#!/bin/bash
# V2p round 3: the 7 still unsolved, resumed from their round-2 states (at the 3600 s CPU cap) with the 13 round-2 proofs
# in the pools and new sibling lemmas added as axioms; +900 abstract s, CPU cap 3600 s more
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/v2_hard loops/V2p --start 3 --rounds 1 --timeout 300,300,900,900 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e19 --keep-out --resume -j 7 --pool original \
  --args="--abstract-time 2000 --max-cpu 3600 --eqhint-stall-cps 120000" > loops/V2p_r3.log 2>&1
echo "V2p r3: $(tail -1 loops/V2p_r3.log) $(date +%T)" | tee loops/V2p_r3.done
