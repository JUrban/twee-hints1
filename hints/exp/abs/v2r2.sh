#!/bin/bash
# V2p round 2: the unsolved, all still on hints when round 1 hit its CPU limit; pools now include the
# 48 round-1 proofs; 900 abstract s, stall gap 60 s (120k CPs), CPU cap 3600 s, states kept (--resume)
until grep -q '^long done' /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/by4jj4ugu.output 2>/dev/null; do sleep 30; done
cd /project/hintwork
echo "start $(date +%T)"
python3 /project/twee/hints/loop.py sets/v2_hard loops/V2p --start 2 --rounds 1 --timeout 300,300,900 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e19 --keep-out --resume -j 18 --pool original \
  --args="--abstract-time 2000 --max-cpu 3600 --eqhint-stall-cps 120000" > loops/V2p_r2.log 2>&1
echo "V2p r2: $(tail -1 loops/V2p_r2.log) $(date +%T)" | tee loops/V2p_r2.done
