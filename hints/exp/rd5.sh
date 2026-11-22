#!/bin/bash
# (22 Nov 15:40) exp61 (notes/2026-11-22-retry-deficit.md): the retry deficit. 300 random unit goals Z8 left unsolved
# (sets/z8u300, seed 60), one fresh 5 s run each in Z8's final context (loops/Z8F.ctx), solve_new.sh's model and
# lemma options, 1 worker: loops/RD5. Starts when the realproofs packer (PID 2235271) ends.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
while kill -0 2235271 2>/dev/null; do sleep 20; done
[ -e loops/RD5 ] && { echo "loops/RD5 exists"; exit 1; }
echo "RD5 start $(date '+%d %T')" > loops/RD5.pids
python3 -u /project/twee/hints/loop.py sets/z8u300 loops/RD5 --init loops/Z8F.ctx --start 1 --rounds 1 --keep-out -j 1 \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout 5 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/RD5.log 2>&1
echo "RD5 done $(date '+%d %T') $(grep -c THM loops/RD5/r1/results.tsv)" >> loops/RD5.pids
