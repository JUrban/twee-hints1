#!/bin/bash
# (22 Nov 14:38) exp59 (notes/2026-11-22-hub-roots.md): the 24 roots with the largest reach among the goals only
# production has (exp/hubroots.py), one fresh 80 s run each in Z8's 6-hour context (loops/Z8F.ctx: Z8's 42,920
# proofs), solve_new.sh's model and lemma options, 1 worker: loops/HUB80.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
[ -e loops/HUB80 ] && { echo "loops/HUB80 exists"; exit 1; }
echo "HUB80 start $(date '+%d %T')" > loops/HUB80.pids
python3 -u /project/twee/hints/loop.py sets/hubroots24 loops/HUB80 --init loops/Z8F.ctx --start 1 --rounds 1 --keep-out -j 1 \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout 80 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/HUB80.log 2>&1
echo "HUB80 done $(date '+%d %T') $(grep -c THM loops/HUB80/r1/results.tsv)" >> loops/HUB80.pids
