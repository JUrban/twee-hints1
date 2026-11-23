#!/bin/bash
# Round 5 continued (15 Nov 01:32): + --far-retry (idle slots retry goals beyond the gaps, fresh, nearest first; far L0 ~12% at 20 s), -j 18, climber J=2. Before: + --fresh-first, -j 16 (fresh 20 s on the climber's first 102 targets: 36 proved, 49/CPU-h vs climber 15; 28/63 of goals with no fresh run in round 5). Before: levels 20,80 only; L1-failed goals go to the live climber (abs/clive.sh): since the restart L2 (resume to 320 s) made 2.5 proofs/CPU-h on 78% of the CPU vs climb 5.3 (sg3), L0 12, L1 10. Before: (23:55) + --sync 60. Before: (22:28) + --retry-hints 1.25 (fresh 20 s retry when the hint pool grew 25%: 3/9 vs 0/12 below 10%; REPORT 2aa). Before: (20:58) + --line-gaps 21,13 (order by proof-line distance; REPORT 2z). Before: (20:15) + --no-eqhint-consider (u3n150: 76 vs 77, ~30% less CPU; REPORT 2y). Before: round 5 continued (14 Nov 19:35) with --no-resume-requeue: on sets/fr100 (100 UL r4 frontier failures, 4 x 20 s
# by resume) BRSn (no requeue) 29 vs BRS (requeue) 23 at the same wall time, BRS-only 0 (REPORT 2w).
# --cascade-continue: the levels round 5 already tried are read from loops/UL/r5/results.tsv. -j 16 (BRS ends soon).
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 20,80 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j 18 --reserve 0 \
  --pool original --wall-factor 15 "$@" --line-gaps 21,13 --retry-hints 1.25 --sync 60 --fresh-first --far-retry --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/UL13.log 2>&1
echo "UL13: $(tail -1 loops/UL13.log) $(date +%T)" | tee loops/UL13.done
