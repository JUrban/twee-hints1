#!/bin/bash
# A/B of the first cascade level (15 Nov 12:55): D = arm dir (reflink copy of loops/UL at 16,416 r5 rows),
# C = --cascade levels (10,80,320 or 5,80,320), 6 workers; otherwise as abs/ul28.sh, without --sync. P = --sched-pmin (default 0.025; UB from 13:09: 0.011, since a 5 s run costs 0.44 of a 10 s one).
# Recent fresh proofs: 84% within 5 abstract s (10k CPs); a 5 s run costs 7.8 wall s against 17.8.
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/all loops/$D --start 5 --cascade $C --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j 6 --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,80 --retry-hints 1.25 --fresh-first --far-retry --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin ${P:-0.025} --retry-knn --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D: $(tail -1 loops/$D.log) $(date +%T)" | tee loops/$D.done
