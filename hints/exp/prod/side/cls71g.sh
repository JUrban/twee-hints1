#!/bin/bash
# (25 Nov) cls71g: cls71f.sh plus --share loops/CLQ83 (SHARE): the 640 s rung's sketch and fill hints too (as clq87c.sh
# shares CLS71's; notes/2026-11-25-time-ladder.md, "hint sharing").
# (25 Nov) cls71f: cls71e.sh plus --final-nopool-ab: the finals of targets with bit 3 of crc32 set get the sketch hints only,
# no pool hints (without production's hints 22 stalled goals at 160,000 pairs: 10 proofs against 11, 14 together, fewer
# pairs on 6 of the 7 both proved; notes/2026-11-25-time-ladder.md, exp88).
# (24 Nov) cls71e: cls71d.sh with -j 10 (J): exp82c ended at 12:59, and the climber, at 2.2-3.5 proofs per CPU h the best
# producer, used all 8 threads; the cap (a climb starts only while fewer than 20 other twee processes run) still holds.
# (24 Nov) cls71d: cls71c.sh plus (1) --final-only-ab: targets with bit 2 of crc32 set get only the 160 s final, the others
# the full climb, to measure what a climb adds to its final (notes/2026-11-23-climber-restart.md, "final-only A/B");
# (2) twee --conditional-encoding fresh: Horn assumptions cost 8x the CPU with the default encoding (exp82), no change
# without them; (3) -j 8 (J): HLW1 ended at 08:48, and the cap (fewer than 20 other twee processes) still holds.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLS71
python3 /project/twee/hints/climb.py sets/all loops/CLS71 --live loops/UL --exclude "${EXCLUDE:-sets/localheads71}" --reclimb "${RECLIMB:-sets/cls71re}" --final-only-ab --final-nopool-ab --share "${SHARE:-/project/hintwork/loops/CLQ83}" \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 20 --sketch-time 5 --final-time "${FINAL:-160}" -j "${J:-10}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" >> loops/CLS71.log 2>&1
echo "CLS71 ended $(date '+%d %T')" >> loops/CLS71.log
