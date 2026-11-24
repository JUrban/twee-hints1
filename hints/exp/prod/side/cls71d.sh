#!/bin/bash
# (24 Nov) cls71d: cls71c.sh plus (1) --final-only-ab: targets with bit 2 of crc32 set get only the 160 s final, the others
# the full climb, to measure what a climb adds to its final (notes/2026-11-23-climber-restart.md, "final-only A/B");
# (2) twee --conditional-encoding fresh: Horn assumptions cost 8x the CPU with the default encoding (exp82), no change
# without them; (3) -j 8 (J): HLW1 ended at 08:48, and the cap (fewer than 20 other twee processes) still holds.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLS71
python3 /project/twee/hints/climb.py sets/all loops/CLS71 --live loops/UL --exclude "${EXCLUDE:-sets/localheads71}" --reclimb "${RECLIMB:-sets/cls71re}" --final-only-ab \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 20 --sketch-time 5 --final-time "${FINAL:-160}" -j "${J:-8}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" >> loops/CLS71.log 2>&1
echo "CLS71 ended $(date '+%d %T')" >> loops/CLS71.log
