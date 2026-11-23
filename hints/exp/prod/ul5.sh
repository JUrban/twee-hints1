#!/bin/bash
# Round 5 of the full loop (14 Nov 17:45) = round 4's cascade restarted: L0 retries had fallen to ~2.8 proofs per
# wall-hour (29 in the last 700 runs) and, having priority, kept the deepening (L1 = 80 s by resume; 4.5/h in U3cas
# on the old binary) from ever starting. --cascade-start 0: the unsolved goals count as tried at 20 s in their
# current context, so the frontier (gap 1) deepens at once; --retry-gap 3: retry only goals at most 3 places
# after a proof (gap 4-10 succeeded 26% on first attempts, less on re-retries).
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 20,80,320,960 --cascade-start 0 --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j 14 --reserve 0 \
  --pool original --wall-factor 15 "$@" --args="--abstract-time 2000" > loops/UL5.log 2>&1
echo "UL5: $(tail -1 loops/UL5.log) $(date +%T)" | tee loops/UL5.done
